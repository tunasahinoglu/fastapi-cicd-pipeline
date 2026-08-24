FROM python:3.12-slim AS builder

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt


FROM python:3.12-slim

RUN apt-get update && apt-get upgrade -y && rm -rf /var/lib/apt/lists/*
RUN groupadd --system appuser && useradd --system --gid appuser appuser

WORKDIR /app

COPY --from=builder /root/.local /home/appuser/.local
COPY app/ ./app/

ENV PATH=/home/appuser/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

RUN chown -R appuser:appuser /app /home/appuser/.local

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]