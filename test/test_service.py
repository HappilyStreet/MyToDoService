import pytest
import requests

BASE_URL = "http://82.117.87.172:30181"

@pytest.fixture
def created_task():
    payload = {"title": "Smoke Test Task", "completed": False, "description": ""}
    r = requests.post(f"{BASE_URL}/tasks", json=payload)
    assert r.status_code == 201
    return r.json()  # возвращаем данные задачи, включая id

def test_get_tasks():
    """Проверяем, что сервис отвечает на GET /tasks"""
    r = requests.get(f"{BASE_URL}/tasks")
    assert r.status_code == 200

def test_create_task(created_task):
    """Проверяем, что задача создана верно"""
    assert created_task["title"] == "Smoke Test Task"
    assert created_task["completed"] is False

def test_delete_task(created_task):
    """Удаляем задачу"""
    task_id = created_task["id"]
    r = requests.delete(f"{BASE_URL}/tasks/{task_id}")
    assert r.status_code == 200

def test_task_not_found_after_delete(created_task):
    """Проверяем, что удалённая задача больше не существует"""
    task_id = created_task["id"]
    # Удаляем на всякий случай, если test_delete_task не вызван
    requests.delete(f"{BASE_URL}/tasks/{task_id}")
    r = requests.get(f"{BASE_URL}/tasks/{task_id}")
    assert r.status_code == 404