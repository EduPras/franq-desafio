from typing import Literal
from rich import print
from langgraph.graph.state import CompiledStateGraph
from langgraph.graph import StateGraph, END

from src.domain.entities.agent import State, StructuredQueryResponse
from src.domain.interfaces.agent import IStructQueryAgent, IVisualizationAgent
from src.domain.interfaces.database import IDatabaseSQL


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

        def error_handler(state: State):
            print("Treating errors")
            errors = state.get("error_messages", [])
            if errors == []:
                errors = ["Erro desconhecido"]
            last_error = errors[-1] if len(errors) >= 1 else errors[0]
            return {
                "error_messages": [f"Erro na tentativa anterior: {last_error}"],
                "success": False
            }

        def check_status(state: State) -> Literal["retry", "continue", "error"]:
            print("Checking the status")
            data = state.get("data")
            retries = state.get("retries", 0)

            if retries >= 4:
                return "error"
            if data == [] or data is None:
                return "retry"
            if not state.get('success'):
                return "retry"
            return "continue"

        def run_llm_struct(state: State):
            struct_resp: StructuredQueryResponse = self.struct_agent.invoke(
                state)

            return {
                "output": struct_resp,
                "queries": [struct_resp.query]
            }

        def todo_vis_node(state: State):
            print(f"Visualizing with type: {state['output'].vis_type}")

            response = self.vis_agent.invoke(state)

            # O código gerado vai para o estado para ser executado no frontend
            return {
                "viz_code": response.code
            }

        wf = StateGraph(State)

        # nodes
        wf.add_node("struct_llm", run_llm_struct)
        wf.add_node("sql_query", self.database.run_query)
        wf.add_node("error_node", error_handler)
        wf.add_node("vis_node", todo_vis_node)
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
        wf.add_edge("vis_node", END)

        return wf.compile()

    def invoke(self, input_text):
        initial_state = State(
            input_text=input_text,
            success=False,
            ddl=self.database.ddl,
            retries=0,
            queries=[],
            error_messages=[]
        )
        return self.workflow.invoke(initial_state)
