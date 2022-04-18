# syntax=docker/dockerfile:1

FROM python:3.8-slim-buster
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . .
CMD uvicorn app.api.server:app --reload --workers 1 --host 0.0.0.0 --port 8000