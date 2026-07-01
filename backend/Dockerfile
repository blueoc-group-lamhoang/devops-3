FROM python:3.11-slim

WORKDIR /app

RUN useradd -m appuser

COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./backend/

WORKDIR /app/backend

USER appuser

EXPOSE 8036

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8036"]