
from src.domain.interfaces.agent import IStructQueryAgent
from src.domain.entities.agent import (
    State, StructuredQueryResponse
)

from src.infrastructure.agents.adapter import LangchainAdapter


class StructurerAgent(IStructQueryAgent):
    def __init__(self, system_prompt: str) -> None:
        llm: LangchainAdapter = LangchainAdapter(
            "Structurer",
            "gemini-2.5-flash", "google-genai",
            system_prompt, StructuredQueryResponse
        )
        super().__init__(llm)

    def invoke(self, state: State) -> StructuredQueryResponse:
        ddl = state.get('ddl')
        question = state.get('input_text')
        errors = state.get("error_messages")
        queries = state.get("queries")
        human_msg = "DDL:\n{ddl}\n\nQuestion: {question}\n\n\
        **ERRORS**:\n{errors}\n\n**ÚLTIMAS QUERIES**:{queries}"
        values = {"ddl": ddl, "question": question,
                  "errors": errors, "queries": queries}

        return self.llm.call(human_msg, values)
