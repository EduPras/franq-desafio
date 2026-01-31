
from src.domain.entities.dtos import QueryResponseDTO
from src.domain.interfaces.agent import IStructQueryAgent

# return a query to use in the database


def input2query(input: str, struct_agent: IStructQueryAgent, db_path: str) -> str:
    pass
