FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY tasks-api/app ./app

EXPOSE 8000

CMD ["uvicorn", "tasks-api.app:app", "--host", "0.0.0.0", "--port", "80"]