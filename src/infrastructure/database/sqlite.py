import sqlite3
from sqlite3 import Cursor, Connection
from typing import Dict

from src.domain.entities.agent import State
from src.domain.interfaces.database import IDatabaseSQL


class SqliteDB(IDatabaseSQL):
    def __init__(self, path: str) -> None:
        super().__init__(path)
        self.ddl = self._get_sql_ddl()

    def _open_conn(self) -> Connection:
        return sqlite3.connect(self.uri)

    def _get_sql_ddl(self) -> str:
        conn = self._open_conn()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "SELECT name, sql FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()

            schema_string = ""
            for table_name, ddl in tables:
                schema_string += f"Table: {table_name}\n{ddl}\n\n"
        except Exception as e:
            print(f'SQL error {e}')
            return ''
        finally:
            conn.close()
        return schema_string

    def run_query(self, state: State) -> Dict:
        conn = self._open_conn()
        cursor = conn.cursor()

        updates = {}
        try:
            query = state.get("queries")[-1]
            cursor.execute(query)
            tables = cursor.fetchall()

            updates["data"] = tables
            updates["success"] = True
            updates["retries"] = state.get("retries", 0) + 1

        except Exception as e:
            print(f'Error: {e}')
            updates["error_messages"] = [str(e)]
            updates["success"] = False
            updates["data"] = None
            updates["retries"] = state.get("retries", 0) + 1

        finally:
            conn.close()

        return updates
