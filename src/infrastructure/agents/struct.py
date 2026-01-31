
from domain.interfaces.agent import IStructQueryAgent
from domain.entities.agent import (
    StructuredQueryCtx, StructuredQueryResponse
)

from infrastructure.agents.adapter import LangchainAdapter

SYSTEM_PROMPT_CONTENT = ""


class StructurerAgent(IStructQueryAgent):
    def __init__(self) -> None:
        llm: LangchainAdapter = LangchainAdapter(
            "Structurer",
            "ministral-3:3b", "ollama",
            SYSTEM_PROMPT_CONTENT, StructuredQueryResponse
        )
        super().__init__(llm)

    def invoke(self, ctx: StructuredQueryCtx) -> StructuredQueryResponse:
        human_msg = "Raw text: {raw_text}"
        values = {"raw_text": ctx.text}

        return self.llm.call(human_msg, values)
