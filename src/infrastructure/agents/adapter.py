
from typing import Any, Dict, Type, TypeVar, cast
from langchain.chat_models import BaseChatModel, init_chat_model
from langchain_core.messages import SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langsmith import traceable
from domain.entities.agent import BaseAgentResponse
from domain.exceptions.base import AIProviderError
from domain.interfaces.agent import ILLM

T = TypeVar("T", bound=BaseAgentResponse)


class LangchainAdapter(ILLM[T]):
    def __init__(
            self,
            name: str,
            model: str,
            provider: str,
            system_prompt: str,
            response_model: Type[T]
    ) -> None:
        super().__init__()
        llm: BaseChatModel = init_chat_model(
            model=model, model_provider=provider, temperature=0)
        self.system_prompt = SystemMessage(system_prompt)
        self.structured_llm = llm.with_structured_output(response_model)
        self.agent_name = name

    def call(self, human_msg: str, values: Dict[str, Any]) -> T:
        return self._traced_call(
            human_msg, values, langsmith_extra={"name": self.agent_name})

    @traceable()
    def _traced_call(self, human_msg: str, values: Dict[str, Any]) -> T:
        prompt_template = ChatPromptTemplate.from_messages(
            [
                self.system_prompt,
                ("human", human_msg),
            ]
        )

        chain = prompt_template | self.structured_llm

        try:
            result = chain.invoke(values)
            return cast(T, result)
        except Exception as e:
            raise AIProviderError(f"LLM provider failed: {e}") from e
