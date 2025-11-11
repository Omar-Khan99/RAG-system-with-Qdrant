# Dockerfile
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="$HOME/.local/bin:$PATH"

WORKDIR /app


RUN apt-get update && apt-get install -y --no-install-recommends \
    curl build-essential git && \
    rm -rf /var/lib/apt/lists/*

COPY pyproject.toml uv.lock ./

RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
    export PATH="$HOME/.local/bin:$PATH" && \
    uv sync --locked

COPY src/ ./src/

EXPOSE 8000

CMD ["sh", "-lc", "uv run uvicorn src.main:app --host 0.0.0.0 --port 8000"]
