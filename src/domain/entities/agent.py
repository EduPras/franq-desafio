from typing import Annotated, Any, Literal
from typing_extensions import NotRequired, TypedDict
from pydantic import BaseModel
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


class State(TypedDict):
    input_text: NotRequired[str]
    ddl: str
    success: bool
    retries: int
    error_messages: Annotated[list, operator.add]
    queries: Annotated[list, operator.add]
    output: NotRequired[StructuredQueryResponse]
    data: NotRequired[Any]
    viz_code: NotRequired[str]
