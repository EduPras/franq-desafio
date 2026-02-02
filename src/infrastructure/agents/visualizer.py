from src.domain.interfaces.agent import IVisualizationAgent
from src.domain.entities.agent import State, VisualizationResponse
from src.infrastructure.agents.adapter import LangchainAdapter
import pandas as pd

SYSTEM_PROMPT_VIS = """Você é um Especialista em Data Science e Streamlit.
### TAREFA
Sua tarefa é gerar exclusivamente código Python para visualizar dados em um dashboard Streamlit.
Você receberá o esquema dos dados (colunas e tipos), uma amostra dos dados e o tipo de gráfico desejado.

### BIBLIOTECAS DISPONÍVEIS:
- `streamlit as st`
- `pandas as pd`
- `plotly.express as px`

### REGRAS CRÍTICAS:
1. **Dados**: Os dados originais estarão disponíveis em uma variável chamada `data` (lista de dicionários). 
2. **DataFrame**: Inicie sempre convertendo os dados: `df = pd.DataFrame(data)`.
3. **Eixos**: Escolha inteligentemente as colunas para os eixos X e Y com base nos nomes e tipos. 
   - Ex: Colunas de data/tempo sempre no eixo X para gráficos de linha.
   - Ex: Colunas numéricas (somas, contagens) sempre no eixo Y.
4. **Interatividade**: Prefira usar `px` (Plotly Express) para gráficos e renderize com st.plotly_chart(fig, width='content'). Não use use_container_width.
5. **Formatação**: Se o tipo for `table`, use `st.dataframe(df, width='content')`. Se for `text`, use `st.metric` ou `st.write`.
6. **Limpeza**: Se houver muitas categorias em um gráfico de pizza/barra (mais de 10), agrupe as menores em 'Outros'.

### FORMATO DE SAÍDA:
- Retorne APENAS o código Python puro.
- Não use blocos de markdown (```python ... ```).
- Não dê explicações.
"""


class VisualizationAgent(IVisualizationAgent):
    def __init__(self) -> None:
        self.llm: LangchainAdapter = LangchainAdapter(
            "Visualizer",
            "gemini-2.0-flash", "google-genai",
            SYSTEM_PROMPT_VIS, VisualizationResponse
        )

    def invoke(self, state: State) -> VisualizationResponse:
        data = state.get("data")
        vis_type = state["output"].vis_type
        user_query = state.get("input_text")

        df_sample = pd.DataFrame(data).head(3)
        schema_info = df_sample.dtypes.to_dict()
        sample_records = df_sample.to_dict(orient="records")

        human_msg = """
        **CONTEXTO**
        Pergunta do Usuário: {query}
        Tipo de Gráfico Solicitado: {vis_type}
        
        **DADOS**
        Esquema (Colunas/Tipos): {schema}
        Amostra (3 linhas): {sample}
        
        Gere o código Python para criar esta visualização no Streamlit.
        """

        values = {
            "query": user_query,
            "vis_type": vis_type,
            "schema": str(schema_info),
            "sample": str(sample_records)
        }

        return self.llm.call(human_msg, values)
