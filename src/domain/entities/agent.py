from typing import Annotated, Any, Literal
from typing_extensions import NotRequired, TypedDict
from pydantic import BaseModel
from enum import Enum
import operator


class BaseAgentContext(BaseModel):
    ...


class BaseAgentResponse(BaseModel):
    ...


class StructuredQueryCtx(BaseAgentContext):
    question: str
    ddl: str


class StructuredQueryResponse(BaseAgentResponse):
    query: str
    vis_type: Literal['bar', 'pie', 'line', 'table', 'text']


class VisualizationResponse(BaseAgentResponse):
    code: str
    reasoning: str


class LLMNodesName(str, Enum):
    STRUCT = "STRUCT"
    VISUALIZATION = "VISUALIZATION"


llm_nodes_list = Literal[LLMNodesName.STRUCT, LLMNodesName.VISUALIZATION]


class State(TypedDict):
    input_text: str
    ddl: str
    success: Annotated[list[llm_nodes_list], operator.add]
    retries: int
    error_messages: Annotated[list, operator.add]
    queries: Annotated[list, operator.add]
    # output: NotRequired[StructuredQueryResponse]
    query: NotRequired[str]
    vis_type: NotRequired[str]
    data: NotRequired[Any]
    viz_code: NotRequired[str]
    reasoning: NotRequired[str]
