FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["sh", "-c", "alembic -c alembic/alembic.ini upgrade head && exec uvicorn app.main:app --host \"${API_HOST:-0.0.0.0}\" --port \"${API_PORT:-8000}\""]
