from pydantic import BaseModel
from src.domain.entities.dtos import QueryStructDTO


class BaseAgentContext(BaseModel):
    ...


class BaseAgentResponse(BaseModel):
    ...


class StructuredQueryCtx(BaseAgentContext):
    text: str


class StructuredQueryResponse(BaseAgentResponse):
    structured_ingredient: QueryStructDTO
