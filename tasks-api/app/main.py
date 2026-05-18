# 1. Импорты
from fastapi import FastAPI, Response, HTTPException
from pydantic import BaseModel
from typing import List
from prometheus_client import Counter

# 2. Определение модели данных (если Task не импортирован из другого файла)
class Task(BaseModel):
    id: int
    title: str
    description: str = None
    completed: bool = False

# 3. Инициализация метрик Prometheus (если используете)
HTTP_REQUESTS = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])

# 4. СОЗДАНИЕ ЭКЗЕМПЛЯРА ПРИЛОЖЕНИЯ - ЭТО САМОЕ ВАЖНОЕ!
app = FastAPI(title="Todo Service", description="API for managing todos")

# 5. Временное хранилище данных (для примера)
tasks = [
    Task(id=1, title="Learn FastAPI", completed=False),
    Task(id=2, title="Deploy to Kubernetes", completed=False)
]

# 6. GET-эндпоинт (для проверки работы)
@app.get("/")
def root():
    return {"message": "Todo Service is running", "tasks_count": len(tasks)}

@app.get("/tasks")
def get_tasks():
    HTTP_REQUESTS.labels(method="GET", endpoint="/tasks", status="200").inc()
    return tasks

# 7. POST-эндпоинт (ваш код)
@app.post("/tasks")
def create_task(task: Task):
    # Проверка на дубликат ID
    if any(t.id == task.id for t in tasks):
        raise HTTPException(status_code=409, detail=f"Task with id {task.id} already exists")
    
    tasks.append(task)
    HTTP_REQUESTS.labels(method="POST", endpoint="/tasks", status="201").inc()
    return task

# 8. DELETE-эндпоинт (ваш код)
@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    global tasks
    # Ищем задачу по ID, а не по индексу
    for i, task in enumerate(tasks):
        if task.id == task_id:
            tasks.pop(i)
            HTTP_REQUESTS.labels(method="DELETE", endpoint="/tasks", status="200").inc()
            return {"deleted": task_id}
    
    # Если задача не найдена
    raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")