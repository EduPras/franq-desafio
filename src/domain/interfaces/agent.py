
from abc import abstractmethod

from typing import TypeVar, Generic, Dict, Any, Type
from abc import ABC

from src.domain.entities.agent import (
    BaseAgentResponse, State, StructuredQueryResponse
)


# T_Context = TypeVar("T_Context", bound=BaseAgentContext)
T_Response = TypeVar("T_Response", bound=BaseAgentResponse)


class ILLM(ABC, Generic[T_Response]):
    def __init__(self) -> None:
        super().__init__()
        self.response_model: Type[T_Response]

    @abstractmethod
    def call(
            self, human_msg: str, values: Dict[str, Any]) -> T_Response:
        ...


class BaseAgent(ABC, Generic[T_Response]):
    name: str = "BaseAgent"
    system_prompt: str

    def __init__(self, llm: ILLM[T_Response]) -> None:
        self.llm = llm
        super().__init__()

    @abstractmethod
    def invoke(self, state: State) -> T_Response: ...


class IStructQueryAgent(
    BaseAgent[StructuredQueryResponse]
):
    def __init__(self, llm: ILLM[StructuredQueryResponse]) -> None:
        super().__init__(llm)
