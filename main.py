from src.domain.entities.agent import State
import streamlit as st
import pandas as pd
import plotly.express as px
from dotenv import load_dotenv
from rich import print

from src.application.use_cases.workflow import Pipeline
from src.infrastructure.agents.struct import StructurerAgent
from src.infrastructure.agents.visualizer import VisualizationAgent

# 1. Configurações iniciais
load_dotenv()
st.set_page_config(page_title="SQL Data Assistant", layout="wide")


def main():
    st.title("📊 SQL Data Assistant")
    st.markdown(
        "Faça perguntas sobre o banco de dados e eu gerarei a query e a visualização.")

    @st.cache_resource
    def get_pipeline():
        struct_agent = StructurerAgent()
        vis_agent = VisualizationAgent()
        return Pipeline(struct_agent, vis_agent)

    pipeline = get_pipeline()

    if "messages" not in st.session_state:
        st.session_state.messages = []

    user_input = st.text_input(
        "Ex: Qual a tendência de reclamações por canal no último ano?")

    if user_input:
        st.session_state.messages.append(
            {"role": "user", "content": user_input})

        with st.spinner("Analisando dados..."):
            print("Analyzing data")
            final_state = pipeline.invoke(user_input)
            st.session_state.messages.append({
                "role": "assistant",
                "content": final_state
            })
    for msg in st.session_state.messages:
        # Use chat_message to create the bubble UI
        with st.chat_message(msg["role"]):
            if msg["role"] == "user":
                st.write(msg["content"])
            else:
                state: State = msg["content"]

                # 1. Display the explanation/answer if available
                if "output" in state:
                    # In your state, explanation might be a separate field or inside output
                    st.write(f"**Query executada:**")
                    st.code(state["output"].query, language="sql")

                # 2. Display the Visualization
                if state.get("data") and "viz_code" in state:
                    render_visualization(state["viz_code"], state["data"])

                # 3. Data Expander
                with st.expander("Ver Dados Brutos"):
                    st.dataframe(state["data"], width='stretch')


def render_visualization(code: str, data: list):
    # Prepare DataFrame and fix types
    df = pd.DataFrame(data)
    for col in df.columns:
        if "utf8" in str(df[col].dtype).lower() or df[col].dtype == "string":
            df[col] = df[col].astype(object)

    context = {
        "st": st,
        "pd": pd,
        "px": px,
        "data": data,
        "df": df
    }

    try:
        # 1. Remove markdown backticks
        clean_code = code.replace("```python", "").replace("```", "").strip()

        # 2. HOTFIX for 2026: Replace deprecated parameter if the LLM hallucinated it
        clean_code = clean_code.replace(
            "use_container_width=True", "width='stretch'")
        clean_code = clean_code.replace(
            "use_container_width=False", "width='content'")

        exec(clean_code, context)
    except Exception as e:
        st.error(f"Erro na execução do código visual: {e}")
        # Show table if chart fails
        st.dataframe(df, width='stretch')


if __name__ == "__main__":
    main()
