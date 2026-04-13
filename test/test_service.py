# test/test_service_real_unique.py
import pytest
import requests
import time

BASE_URL = "http://82.117.87.172:30181"

# ---------------------------
# Генератор уникальных ID
# ---------------------------
def unique_id():
    # Используем timestamp, чтобы был уникальным
    return int(time.time() * 1000) % 1000000

# ---------------------------
# Вспомогательная функция для polling
# ---------------------------
def wait_until_task_gone(task_id, timeout=3, interval=0.1):
    """Ждём, пока задача исчезнет из списка задач."""
    end_time = time.time() + timeout
    while time.time() < end_time:
        r = requests.get(f"{BASE_URL}/tasks")
        if r.status_code == 200:
            tasks = r.json()
            ids = [t["id"] for t in tasks]
            if task_id not in ids:
                return True
        time.sleep(interval)
    return False

# ---------------------------
# Фикстура для создания задачи
# ---------------------------
@pytest.fixture
def created_task():
    task_id = unique_id()
    data = {"id": task_id, "title": "Smoke Test Task", "completed": False}
    r = requests.post(f"{BASE_URL}/tasks", json=data)
    assert r.status_code == 200
    return r.json()

# ---------------------------
# Тест создания задачи
# ---------------------------
def test_create_task():
    task_id = unique_id()
    data = {"id": task_id, "title": "Another Task", "completed": False}
    r = requests.post(f"{BASE_URL}/tasks", json=data)
    assert r.status_code == 200
    resp_data = r.json()
    assert resp_data["id"] == task_id
    assert resp_data["title"] == "Another Task"
    assert resp_data["completed"] is False

# ---------------------------
# Тест удаления задачи
# ---------------------------
def test_delete_task(created_task):
    task_id = created_task["id"]
    r = requests.delete(f"{BASE_URL}/tasks/{task_id}")
    assert r.status_code == 200
    resp_data = r.json()
    assert resp_data["deleted"] == task_id

    # Ждём, пока задача исчезнет
    assert wait_until_task_gone(task_id), f"Task {task_id} still exists after deletion"

# ---------------------------
# Тест проверки отсутствия задачи после удаления
# ---------------------------
def test_task_not_found_after_delete():
    task_id = unique_id()
    # создаём задачу
    requests.post(f"{BASE_URL}/tasks", json={"id": task_id, "title": "Temp Task", "completed": False})
    # удаляем задачу
    requests.delete(f"{BASE_URL}/tasks/{task_id}")
    # ждём, пока задача исчезнет
    assert wait_until_task_gone(task_id), f"Task {task_id} still exists after deletion"
