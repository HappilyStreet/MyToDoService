# test/test_service_real.py
import pytest
import requests

# Адрес твоего реального сервера
BASE_URL = "http://82.117.87.172:30181"

# ---------------------------
# Фикстура: создаём задачу перед тестами
# ---------------------------
@pytest.fixture
def created_task():
    """Создаём задачу перед тестами и возвращаем её"""
    data = {"id": 1, "title": "Smoke Test Task", "completed": False}
    r = requests.post(f"{BASE_URL}/tasks", json=data)
    assert r.status_code == 201  # FastAPI возвращает 201 при создании
    return r.json()

# ---------------------------
# Тест: создание задачи
# ---------------------------
def test_create_task():
    data = {"id": 2, "title": "Another Task", "completed": False}
    r = requests.post(f"{BASE_URL}/tasks", json=data)
    assert r.status_code == 201
    resp_data = r.json()
    assert resp_data["id"] == 2
    assert resp_data["title"] == "Another Task"
    assert resp_data["completed"] is False

# ---------------------------
# Тест: удаление задачи
# ---------------------------
def test_delete_task(created_task):
    task_id = created_task["id"]
    r = requests.delete(f"{BASE_URL}/tasks/{task_id}")
    assert r.status_code == 200
    resp_data = r.json()
    assert resp_data["deleted"] == task_id

# ---------------------------
# Тест: проверка, что задача удалена
# ---------------------------
def test_task_not_found_after_delete(created_task):
    task_id = created_task["id"]
    # сначала удаляем
    requests.delete(f"{BASE_URL}/tasks/{task_id}")
    # потом проверяем, что задача больше не существует
    r = requests.get(f"{BASE_URL}/tasks")
    assert r.status_code == 200
    tasks = r.json()
    ids = [t["id"] for t in tasks]
    assert task_id not in ids