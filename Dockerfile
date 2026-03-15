# FinRobot — Dockerfile
# Usa uv para resolución rápida de dependencias

# ═══════════════════════════════════════════════
# Stage 1: Builder (instalar dependencias con uv)
# ═══════════════════════════════════════════════
FROM python:3.11-slim AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Instalar uv (resolución de deps ultrarrápida)
RUN pip install --no-cache-dir uv

WORKDIR /app

# Instalar dependencias con uv (mucho más rápido que pip)
# Nota: usamos torch CPU-only en Docker — la GPU se accede via Ollama
COPY requirements-docker.txt .
RUN uv pip install --system --no-cache \
    --extra-index-url https://download.pytorch.org/whl/cpu \
    --index-strategy unsafe-best-match \
    -r requirements-docker.txt

# ═══════════════════════════════════════════════
# Stage 2: Runtime
# ═══════════════════════════════════════════════
FROM python:3.11-slim AS runtime

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiar paquetes Python instalados desde builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copiar código fuente
COPY . .

# Añadir /app al PYTHONPATH en vez de pip install -e .
# (evita que setup.py resuelva requirements.txt completo)
ENV PYTHONPATH="/app:${PYTHONPATH}"

# Directorio de trabajo para los agentes
RUN mkdir -p /app/coding /app/output

# Variables de entorno por defecto
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Health check: verificar que FinRobot se importa correctamente
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD python -c "from finrobot.llm_config import get_ollama_config; print('OK')" || exit 1

# Entrypoint por defecto: shell interactivo
CMD ["python"]
