from typing import Dict
from rich import print
import sqlite3


def get_db_schema(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Busca o nome das tabelas e o comando SQL que as criou (DDL)
    cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    schema_string = ""
    for table_name, ddl in tables:
        schema_string += f"Table: {table_name}\n{ddl}\n\n"

    conn.close()
    return schema_string


def main():
    print("Hello from franq!")
    # Pipeline
    # question: str = some_input()
    # output: Dict[Any, Any] = llm_pipeline(question)


if __name__ == "__main__":
    main()
    print(get_db_schema('data/anexo_desafio_1.db'))
