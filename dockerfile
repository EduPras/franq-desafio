FROM python:3.13-slim-bookworm

ARG STREAMLIT_PORT=8501
ENV PORT=$STREAMLIT_PORT

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin

ADD . /app

WORKDIR /app

RUN uv sync --locked

EXPOSE 8501

CMD uv run streamlit run main.py --server.address 0.0.0.0 --server.port $PORT
