FROM python:3.11-slim

# Install uv (blazing-fast Rust package installer)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Install build-essential for packages requiring compilation
RUN apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*

# Install dependencies using uv
COPY requirements.txt .
RUN uv pip install --system --no-cache -r requirements.txt

# Copy application code (including pre-populated SQLite DB)
COPY . .

# Warm up the local embedding model cache
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('BAAI/bge-small-en-v1.5')"

CMD ["sh", "-c", "PYTHONPATH=. python scripts/update_metadata_only.py && uvicorn main:app --host 0.0.0.0 --port 8000"]
