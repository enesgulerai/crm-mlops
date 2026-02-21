# ==========================================
# STAGE 1: BUILDER
# ==========================================
FROM python:3.11-slim AS builder

WORKDIR /app

RUN python -m venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH"

COPY src/ui/requirements.txt ./requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

# ==========================================
# STAGE 2: RUNTIME
# ==========================================
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

WORKDIR /app

COPY --from=builder /opt/venv /opt/venv

COPY . .

RUN adduser --disabled-password --gecos "" uiuser && chown -R uiuser /app
USER uiuser

EXPOSE 8501

CMD ["streamlit", "run", "src/ui/interface.py", "--server.port=8501", "--server.address=0.0.0.0"]