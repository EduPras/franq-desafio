from typing import final
import streamlit as st
import pandas as pd
import plotly.express as px
from dotenv import load_dotenv

from src.services import Pipeline
from src.infrastructure import (
    StructurerAgent, VisualizationAgent, SqliteDB
)
from src.utils.markdown import import_markdown_as_string

STRUCT_PROMPT = './prompts/struct_agent.md'
VIS_PROMPT = './prompts/visualizer_agent.md'

load_dotenv()

st.set_page_config(page_title="Franq - SQL chat", layout="centered")


def main():
    st.title("Franq - SQL chat")

    @st.cache_resource
    def get_pipeline():
        return Pipeline(
            StructurerAgent(import_markdown_as_string(STRUCT_PROMPT)),
            VisualizationAgent(import_markdown_as_string(VIS_PROMPT)),
            SqliteDB('data/anexo_desafio_1.db')
        )

    pipeline = get_pipeline()

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            if msg["role"] == "user":
                st.markdown(msg["content"])
            else:
                state = msg["content"]

                if "reasoning" in state:
                    st.markdown(state["reasoning"])

                if "query" in state:
                    st.markdown(f"**Query SQL gerada:**")
                    st.code(state["query"], language="sql")

                if state.get("data") and "viz_code" in state:
                    render_visualization(state["viz_code"], state["data"])

                with st.expander("Ver tabela de dados"):
                    st.dataframe(state["data"], width='content')

    if prompt := st.chat_input("Como posso ajudar com os dados hoje?"):
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Consultando banco de dados..."):
                final_state = pipeline.invoke(prompt)

                if "reasoning" in final_state:
                    st.markdown(final_state["reasoning"])
                if "query" in final_state:
                    st.code(final_state["query"], language="sql")

                if final_state.get("data") and "viz_code" in final_state:
                    render_visualization(
                        final_state["viz_code"], final_state["data"])

                st.session_state.messages.append(
                    {"role": "assistant", "content": final_state})


def render_visualization(code: str, data: list):
    df = pd.DataFrame(data)
    # Type clean for arrow
    for col in df.columns:
        if "utf8" in str(df[col].dtype).lower() or df[col].dtype == "string":
            df[col] = df[col].astype(object)

    context = {"st": st, "pd": pd, "px": px, "data": data, "df": df}

    try:
        clean_code = code.replace("```python", "").replace("```", "").strip()

        clean_code = clean_code.replace("width='stretch'", "width='content'")
        clean_code = clean_code.replace(
            "use_container_width=True", "width='content'")

        exec(clean_code, context)
    except Exception as e:
        st.error(f"Erro visual: {e}")
        st.dataframe(df, width='content')


if __name__ == "__main__":
    main()
