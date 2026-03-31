import requests
import random

BASE_URL = "http://82.117.87.172:30181"

def generate_unique_id():
    """Генерируем уникальный id для каждой задачи"""
    return random.randint(10000, 99999)

def test_get_tasks():
    """Проверяем, что сервис отвечает на GET /tasks"""
    r = requests.get(f"{BASE_URL}/tasks")
    assert r.status_code == 200

def test_create_task():
    """Создаём задачу и проверяем, что она верно возвращается"""
    task_id = generate_unique_id()
    payload = {
        "id": task_id,
        "title": "Smoke Test Task",
        "completed": False
    }
    r = requests.post(f"{BASE_URL}/tasks", json=payload)
    assert r.status_code == 201, f"Ошибка создания задачи: {r.text}"

    data = r.json()
    assert data["id"] == task_id
    assert data["title"] == "Smoke Test Task"
    assert data["completed"] is False

    # Возвращаем id для следующих тестов
    return task_id

def test_delete_task():
    """Удаляем задачу, созданную выше"""
    task_id = test_create_task()  # создаём задачу перед удалением
    r = requests.delete(f"{BASE_URL}/tasks/{task_id}")
    assert r.status_code == 200, f"Ошибка удаления задачи: {r.text}"

def test_task_not_found_after_delete():
    """Проверяем, что удалённая задача больше не существует"""
    task_id = test_create_task()  # создаём задачу перед удалением
    requests.delete(f"{BASE_URL}/tasks/{task_id}")  # удаляем задачу

    r = requests.get(f"{BASE_URL}/tasks/{task_id}")
    assert r.status_code == 404, f"Задача не удалена: {r.text}"