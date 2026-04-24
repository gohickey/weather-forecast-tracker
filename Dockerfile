FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
# TODO: switch to uv
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ .
COPY config.json .

EXPOSE 8000

CMD ["python", "main.py"]
