from fastapi import FastAPI, Request
from prometheus_fastapi_instrumentator import Instrumentator
import uvicorn

app = FastAPI()

# Автоматический сбор метрик
Instrumentator().instrument(app).expose(app)

todos = []

@app.get("/tasks")
def get_tasks():
    return todos

@app.post("/tasks")
def add_task(request: Request):
    data = request.json()
    todos.append(data)
    return data

@app.delete("/tasks/{index}")
def delete_task(index: int):
    if 0 <= index < len(todos):
        task = todos.pop(index)
        return task
    return {"error": "Not found"}, 404

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=80)