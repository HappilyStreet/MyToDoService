import requests

BASE_URL = "http://82.117.87.172:30181"

def test_get_tasks():
    """Проверяем, что сервис отвечает на GET /tasks"""
    r = requests.get(f"{BASE_URL}/tasks")
    assert r.status_code == 200

def test_create_task():
    """Создаём задачу и проверяем, что она верно возвращается"""
    payload = {"title": "Smoke Test Task", "completed": False}
    r = requests.post(f"{BASE_URL}/tasks", json=payload)
    assert r.status_code == 201
    data = r.json()
    assert data["title"] == "Smoke Test Task"
    assert data["completed"] is False
    # Сохраняем id для удаления
    global task_id
    task_id = data["id"]

def test_delete_task():
    """Удаляем задачу, созданную выше"""
    r = requests.delete(f"{BASE_URL}/tasks/{task_id}")
    assert r.status_code == 200

def test_task_not_found_after_delete():
    """Проверяем, что удалённая задача больше не существует"""
    r = requests.get(f"{BASE_URL}/tasks/{task_id}")
    assert r.status_code == 404