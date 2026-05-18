import pytest
import requests
import time
import uuid

# Фиксированный URL (без переменных окружения)
BASE_URL = "http://193.233.246.93:30181"

# ---------------------------
# Генератор уникальных ID
# ---------------------------
def unique_id():
    """Генерирует гарантированно уникальный ID"""
    return int(uuid.uuid4().int % 1_000_000)

# ---------------------------
# Вспомогательная функция для polling
# ---------------------------
def wait_until_task_gone(task_id, timeout=5, interval=0.1):
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
    """Создаёт задачу и удаляет её после теста"""
    task_id = unique_id()
    data = {"id": task_id, "title": "Smoke Test Task", "completed": False}
    r = requests.post(f"{BASE_URL}/tasks", json=data)
    assert r.status_code == 200, f"Failed to create task: {r.text}"
    task = r.json()
    assert task["id"] == task_id
    
    yield task
    
    # Teardown: удаляем задачу после теста
    requests.delete(f"{BASE_URL}/tasks/{task_id}")
    wait_until_task_gone(task_id)

# ---------------------------
# Тест 1: Создание задачи (счастливый путь)
# ---------------------------
def test_create_task():
    task_id = unique_id()
    data = {"id": task_id, "title": "Another Task", "completed": False}
    r = requests.post(f"{BASE_URL}/tasks", json=data)
    
    assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
    resp_data = r.json()
    assert resp_data["id"] == task_id
    assert resp_data["title"] == "Another Task"
    assert resp_data["completed"] is False
    
    # Cleanup
    requests.delete(f"{BASE_URL}/tasks/{task_id}")

# ---------------------------
# Тест 2: Создание задачи без поля completed (должен быть default False)
# ---------------------------
def test_create_task_without_completed():
    task_id = unique_id()
    data = {"id": task_id, "title": "No Completed Field"}
    r = requests.post(f"{BASE_URL}/tasks", json=data)
    
    assert r.status_code == 200
    resp_data = r.json()
    assert resp_data["id"] == task_id
    assert resp_data["title"] == "No Completed Field"
    assert resp_data["completed"] is False  # default value
    
    requests.delete(f"{BASE_URL}/tasks/{task_id}")

# ---------------------------
# Тест 3: Создание задачи без title (ДОЛЖЕН ВОЗВРАЩАТЬ 422)
# ---------------------------
def test_create_task_without_title():
    task_id = unique_id()
    data = {"id": task_id, "completed": False}
    r = requests.post(f"{BASE_URL}/tasks", json=data)
    
    assert r.status_code == 422, f"Expected 422 validation error, got {r.status_code}"
    error_data = r.json()
    assert "title" in str(error_data)  # Ошибка должна упоминать поле title

# ---------------------------
# Тест 4: Создание задачи с существующим ID (ДОЛЖЕН ВОЗВРАЩАТЬ 409 или 400)
# ---------------------------
def test_create_duplicate_id():
    task_id = unique_id()
    data = {"id": task_id, "title": "First Task"}
    
    # Создаём первую задачу
    r1 = requests.post(f"{BASE_URL}/tasks", json=data)
    assert r1.status_code == 200
    
    # Пытаемся создать вторую с тем же ID
    r2 = requests.post(f"{BASE_URL}/tasks", json=data)
    
    # Ожидаем ошибку (409 Conflict или 400 Bad Request)
    assert r2.status_code in [400, 409, 422], \
        f"Duplicate ID should fail, got {r2.status_code}"
    
    # Cleanup
    requests.delete(f"{BASE_URL}/tasks/{task_id}")

# ---------------------------
# Тест 5: Удаление существующей задачи
# ---------------------------
def test_delete_task(created_task):
    task_id = created_task["id"]
    
    r = requests.delete(f"{BASE_URL}/tasks/{task_id}")
    assert r.status_code == 200
    
    time.sleep(0.5)  # Подождать полсекунды
    
    # Проверяем, что задача действительно удалена
    r_get = requests.get(f"{BASE_URL}/tasks/{task_id}")
    assert r_get.status_code == 404

# ---------------------------
# Тест 6: Удаление несуществующей задачи (ДОЛЖЕН ВОЗВРАЩАТЬ 404)
# ---------------------------
def test_delete_nonexistent_task():
    fake_id = 999999999
    r = requests.delete(f"{BASE_URL}/tasks/{fake_id}")
    
    # После исправления сервера должно быть 404
    assert r.status_code == 404, f"Expected 404, got {r.status_code}"

# ---------------------------
# Тест 7: Проверка исчезновения задачи после удаления
# ---------------------------
def test_task_not_found_after_delete():
    task_id = unique_id()
    
    r_create = requests.post(f"{BASE_URL}/tasks",
                            json={"id": task_id, "title": "Temp Task", "completed": False})
    assert r_create.status_code == 200
    
    r_delete = requests.delete(f"{BASE_URL}/tasks/{task_id}")
    assert r_delete.status_code == 200
    
    time.sleep(0.5)  # Подождать
    
    r_get = requests.get(f"{BASE_URL}/tasks/{task_id}")
    assert r_get.status_code == 404