
from src.domain.interfaces.agent import IStructQueryAgent
from src.domain.entities.agent import (
    State, StructuredQueryResponse
)

from src.infrastructure.agents.adapter import LangchainAdapter


SYSTEM_PROMPT_CONTENT = """Você é um Especialista em SQLite e dashboards.
### TAREFA
1. **Consulta SQL**: Converter perguntas em linguagem natural em queries SQL precisas.
2. **Tipo de visualização**: Definir o tipo de visualização com base no que é pedido no input.
, valores entre (``table``, ``pie``,  ``bar``,  ``line`` ou ``text``).
3. **Correção**: Caso você gere uma query errada, você recebe um histórico de queries e mensagens de erro.
Utilize essas informações para corrigir e gerar uma nova query correta.

### BANCO DE DADOS (DDL):
{ddl}

### REGRAS CRÍTICAS:
1. **Filtro de Entidades**: Identifique todas as entidades mencionadas (ex: 'WhatsApp', 'App', 'Maio', '2024'). Cada entidade deve se tornar um filtro `WHERE`.
2. **Mapeamento de Ações**:
   - "Interagiram" -> `interagiu = 1` ou `interagiu IS TRUE`.
   - "Resolvidas" -> `resolvido = 1`.
3. **Case Sensitivity & LOWER**: Sempre use `LOWER(coluna) = LOWER('valor')` para colunas de texto (canal, categoria, profissão, etc).
4. **Tratamento de Datas (Sintaxe SQLite)**:
   - Ano específico: `strftime('%Y', data_coluna) = '2024'`
   - Mês específico: `strftime('%m', data_coluna) = '05'`
5. **Contagem Única**: Use `COUNT(DISTINCT cliente_id)` para perguntas sobre "quantidade de clientes".
6. **Dataframe**: O retorno da query será usado posteriormente para a criação de um dataframe.

### EXEMPLO DE RACIOCÍNIO:
Pergunta: "Quantos clientes interagiram com campanhas de WhatsApp em 2024?"
Passos:
- Tabela: `campanhas_marketing`
- Filtro 1: `LOWER(canal) = LOWER('WhatsApp')`
- Filtro 2: `interagiu = 1` (ação de interagir)
- Filtro 3: `strftime('%Y', data_envio) = '2024'` (ano)

### FORMATO DE SAÍDA:
- Retorne APENAS o código SQL puro, sem explicações ou blocos de markdown.
- Tipo de visualização.
- O output da query deve ser compatível com pandas, ou seja, possível de transformar em um dataframe.
"""


class StructurerAgent(IStructQueryAgent):
    def __init__(self) -> None:
        llm: LangchainAdapter = LangchainAdapter(
            "Structurer",
            "gemini-2.5-flash", "google-genai",
            SYSTEM_PROMPT_CONTENT, StructuredQueryResponse
        )
        super().__init__(llm)

    def invoke(self, state: State) -> StructuredQueryResponse:
        ddl = state.get('ddl')
        question = state.get('input_text')
        errors = state.get("error_messages")
        queries = state.get("queries")
        human_msg = "DDL:\n{ddl}\n\nQuestion: {question}\n\n\
        **ERRORS**:\n{errors}\n\n**ÚLTIMAS QUERIES**:{queries}"
        values = {"ddl": ddl, "question": question,
                  "errors": errors, "queries": queries}

        return self.llm.call(human_msg, values)
