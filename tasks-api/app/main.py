# Импорт HTTPException добавьте в начало файла
from fastapi import FastAPI, Response, HTTPException

# ЗАМЕНИТЕ существующий POST-эндпоинт
@app.post("/tasks")
def create_task(task: Task):
    # Проверка на дубликат ID
    if any(t.id == task.id for t in tasks):
        raise HTTPException(status_code=409, detail=f"Task with id {task.id} already exists")
    
    tasks.append(task)
    HTTP_REQUESTS.labels(method="POST", endpoint="/tasks", status="201").inc()
    return task

# ЗАМЕНИТЕ существующий DELETE-эндпоинт
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