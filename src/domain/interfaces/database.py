
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict

from src.domain.entities.agent import State


class IDatabaseSQL(ABC):
    def __init__(self, path: str) -> None:
        self.uri: Path = Path(path)
        self.ddl: str

    @abstractmethod
    def _get_sql_ddl(self) -> str: ...

    @abstractmethod
    def run_query(self, state: State) -> Dict: ...
