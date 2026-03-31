from fastapi import FastAPI, Response
from typing import List
from app.models import Task
import os

# Для метрик Prometheus1
from prometheus_client import Counter, generate_latest, CollectorRegistry, CONTENT_TYPE_LATEST, push_to_gateway

app = FastAPI(title="Task API")

# ---------------------------
# Сервис и версия
# ---------------------------
SERVICE_NAME = os.getenv("SERVICE_NAME", "task-api")
VERSION = os.getenv("VERSION", "1.0")

# ---------------------------
# Список задач
# ---------------------------
tasks: List[Task] = []

# ---------------------------
# Prometheus метрики
# ---------------------------
registry = CollectorRegistry()

HTTP_REQUESTS = Counter(
    'http_requests_total', 
    'Total HTTP requests',
    ['method', 'endpoint', 'status'],
    registry=registry
)

PUSHGATEWAY_URL = os.getenv("PUSHGATEWAY_URL", "pushgateway:9091")

# ---------------------------
# Эндпоинт для метрик
# ---------------------------
@app.get("/metrics")
def metrics():
    return Response(content=generate_latest(registry), media_type=CONTENT_TYPE_LATEST)

# ---------------------------
# Основные маршруты
# ---------------------------
@app.get("/")
def root():
    HTTP_REQUESTS.labels(method="GET", endpoint="/", status="200").inc()
    return {"service": SERVICE_NAME, "version": VERSION}

@app.get("/health")
def health():
    HTTP_REQUESTS.labels(method="GET", endpoint="/health", status="200").inc()
    return {"status": "ok"}

@app.get("/tasks")
def get_tasks():
    HTTP_REQUESTS.labels(method="GET", endpoint="/tasks", status="200").inc()
    return tasks

@app.post("/tasks")
def create_task(task: Task):
    tasks.append(task)
    HTTP_REQUESTS.labels(method="POST", endpoint="/tasks", status="201").inc()
    # Пушим метрики сразу в Pushgateway
    push_to_gateway(PUSHGATEWAY_URL, job=SERVICE_NAME, registry=registry)
    return task

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    global tasks
    tasks = [t for t in tasks if t.id != task_id]
    HTTP_REQUESTS.labels(method="DELETE", endpoint="/tasks", status="200").inc()
    push_to_gateway(PUSHGATEWAY_URL, job=SERVICE_NAME, registry=registry)
    return {"deleted": task_id}