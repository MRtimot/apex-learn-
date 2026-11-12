FROM python:3.9-slim

WORKDIR /app

COPY . /app

EXPOSE 8000

ENV PORT=8000

CMD ["python3", "server.py"]
