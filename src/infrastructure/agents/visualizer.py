from src.domain.interfaces.agent import IStructQueryAgent
from src.domain.entities.agent import (
    State, StructuredQueryResponse
)

from src.infrastructure.agents.adapter import LangchainAdapter


SYSTEM_PROMPT_CONTENT = """Você é um Especialista em SQLite.
Sua tarefa é converter perguntas em linguagem natural em queries SQL precisas.

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

### EXEMPLO DE RACIOCÍNIO:
Pergunta: "Quantos clientes interagiram com campanhas de WhatsApp em 2024?"
Passos:
- Tabela: `campanhas_marketing`
- Filtro 1: `LOWER(canal) = LOWER('WhatsApp')`
- Filtro 2: `interagiu = 1` (ação de interagir)
- Filtro 3: `strftime('%Y', data_envio) = '2024'` (ano)

### FORMATO DE SAÍDA:
- Retorne APENAS o código SQL puro, sem explicações ou blocos de markdown.
"""


class VisualizerAgent(IVisualizerAgent):
    def __init__(self) -> None:
        llm: LangchainAdapter = LangchainAdapter(
            "Visualizer",
            "gemini-2.5-flash", "google-genai",
            SYSTEM_PROMPT_CONTENT, StructuredQueryResponse
        )
        super().__init__(llm)

    def invoke(self, state: State) -> VisualizerResponse:
        ddl = state.get('ddl')
        input_text = state.get('input_text')
        question = state.get('input_text')
        human_msg = "DDL:\n{ddl}\n\nQuestion: {question}"
        values = {"ddl": ddl, "question": question}

        return self.llm.call(human_msg, values)
