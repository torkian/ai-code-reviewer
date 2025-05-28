FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PORT=5000

EXPOSE ${PORT}

CMD gunicorn --bind 0.0.0.0:${PORT} app:app