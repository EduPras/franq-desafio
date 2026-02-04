from typing import Literal
import logging
from langgraph.graph.state import CompiledStateGraph
from langgraph.graph import StateGraph, END

from src.config.logger import LoggerBuilder
from src.domain.entities.agent import LLMNodesName, State, StructuredQueryResponse
from src.domain.exceptions.base import AIProviderError
from src.domain.interfaces.agent import IStructQueryAgent, IVisualizationAgent
from src.domain.interfaces.database import IDatabaseSQL


logger_builder = LoggerBuilder(__name__, logging.DEBUG)
logger = logger_builder.getLogger()


class Pipeline():
    def __init__(
            self,
            struct_agent: IStructQueryAgent,
            vis_agent: IVisualizationAgent,
            database: IDatabaseSQL
    ) -> None:
        self.struct_agent: IStructQueryAgent = struct_agent
        self.vis_agent: IVisualizationAgent = vis_agent
        self.database: IDatabaseSQL = database
        self.workflow: CompiledStateGraph = self._build_workflow()

    def _build_workflow(self) -> CompiledStateGraph:
        logger.info("Building workflow")
        # Nodes

        def error_handler(state: State):
            errors = state.get("error_messages", [])
            if errors == []:
                errors = ["Erro desconhecido"]
            last_error = errors[-1]

            logger.error(f"Handling error: {last_error}")
            return {
                "error_messages": [f"Erro na tentativa anterior: {last_error}"],
            }

        def check_status(state: State) -> Literal["retry", "continue", "error"]:
            logger.info("Checking pipeline status")
            data = state.get("data")
            retries = state.get("retries", 0)

            if retries >= 4:
                return "error"
            if data == [] or data is None:
                return "retry"
            return "continue"

        def run_llm_struct(state: State):
            logger.info(f"Sending '{state["input_text"]}' with {
                        len(state['error_messages'])} previous errors and {len(state['queries'])}")
            struct_resp: StructuredQueryResponse = self.struct_agent.invoke(
                state)

            return {
                "query": struct_resp.query,
                "vis_type": struct_resp.vis_type,
                "queries": [struct_resp.query]
            }

        def vis_node(state: State):
            logger.info("Invoking Visualizer agent")
            try:
                response = self.vis_agent.invoke(state)
                if response.code is not None:
                    return {
                        "viz_code": response.code,
                        "reasoning": response.reasoning,
                        "success": [LLMNodesName.VISUALIZATION]
                    }

            except AIProviderError:
                logger.error("Error requesting API model. Try again.")

        def audit_node(state: State):
            logger.info(f"Pipeline finished with stats {state["success"]}")
            logger.info(state)

        # Workflow
        wf = StateGraph(State)

        # nodes
        wf.add_node("struct_llm", run_llm_struct)
        wf.add_node("sql_query", self.database.run_query)
        wf.add_node("error_node", error_handler)
        wf.add_node("vis_node", vis_node)
        wf.add_node("audit_node", audit_node)
        # edges / connections
        wf.set_entry_point("struct_llm")
        wf.add_edge("struct_llm", "sql_query")
        # loop for handling errors
        wf.add_conditional_edges(
            "sql_query",
            check_status,
            {
                "retry": "error_node",
                "continue": "vis_node",
                "error": END
            }
        )
        wf.add_edge("error_node", "struct_llm")
        wf.add_edge("vis_node", "audit_node")
        wf.add_edge("audit_node", END)

        return wf.compile()

    def invoke(self, input_text):
        logger.info(f"Invoking text2sql with input: {input_text}")
        initial_state = State(
            input_text=input_text,
            success=[],
            ddl=self.database.ddl,
            retries=0,
            queries=[],
            error_messages=[]
        )
        return self.workflow.invoke(initial_state)
