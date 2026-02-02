from pathlib import Path
import sqlite3

from src.domain.entities.agent import State


def get_sql_ddl(path: Path) -> str:
    conn = sqlite3.connect(path)
    cursor = conn.cursor()

    cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    schema_string = ""
    for table_name, ddl in tables:
        schema_string += f"Table: {table_name}\n{ddl}\n\n"

    conn.close()
    return schema_string


def run_query(state: State):
    path = Path('data/anexo_desafio_1.db')
    conn = sqlite3.connect(path)
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


if __name__ == '__main__':
    run_query(Path('./data/anexo_desafio_1.db'))
