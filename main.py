from rich import print
from dotenv import load_dotenv

from src.application.use_cases.workflow import Pipeline
from src.infrastructure.agents.struct import StructurerAgent

load_dotenv()


def main():
    struct_agent = StructurerAgent()
    pipeline = Pipeline(struct_agent)

    input = "Quantos clientes interagiram com campanhas de WhatsApp em 2024?"
    input = "Quais categorias de produto tiveram o maior número de compras em média por cliente?"
    input = "Qual o número de reclamações não resolvidas por canal?"
    input = "Qual a tendência de reclamações por canal no último ano?"
    response = pipeline.invoke(input)
    print(response)


if __name__ == "__main__":
    main()
