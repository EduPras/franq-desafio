from src.domain.interfaces.agent import IVisualizationAgent
from src.domain.entities.agent import State, VisualizationResponse
from src.infrastructure.agents.adapter import LangchainAdapter
import pandas as pd


class VisualizationAgent(IVisualizationAgent):
    def __init__(self, system_prompt: str) -> None:
        self.llm: LangchainAdapter = LangchainAdapter(
            "Visualizer",
            "gemini-2.0-flash", "google-genai",
            system_prompt, VisualizationResponse
        )

    def invoke(self, state: State) -> VisualizationResponse:
        data = state.get("data")
        vis_type = state.get("vis_type")
        input_text = state.get("input_text")
        query = state.get("queries")[-1]

        df_sample = pd.DataFrame(data).head(3)
        schema_info = df_sample.dtypes.to_dict()
        sample_records = df_sample.to_dict(orient="records")

        human_msg = """
        **CONTEXTO**
        Pergunta do Usuário: {input_text}
        Tipo de Gráfico Solicitado: {vis_type}
        
        **DADOS**
        Query: {query}
        Esquema (Colunas/Tipos): {schema}
        Amostra (3 linhas): {sample}
        
        Gere o código Python para criar esta visualização no Streamlit.
        """

        values = {
            "input_text": input_text,
            "query": query,
            "vis_type": vis_type,
            "schema": str(schema_info),
            "sample": str(sample_records)
        }

        return self.llm.call(human_msg, values)
