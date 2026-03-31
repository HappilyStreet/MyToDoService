import pytest
import requests
import uuid

BASE_URL = "http://localhost:8000"  # Укажи свой URL сервиса


@pytest.fixture
def task_payload():
    """Генерируем уникальную задачу"""
    task_id = uuid.uuid4().int >> 64  # Числовой ID для FastAPI
    return {
        "id": task_id,
        "title": "Smoke Test Task",
        "completed": False
    }


@pytest.fixture
def created_task(task_payload):
    """Создаём задачу перед тестом и возвращаем payload"""
    r = requests.post(f"{BASE_URL}/tasks", json=task_payload)
    assert r.status_code == 200, f"Ошибка создания задачи: {r.text}"
    return task_payload


def test_create_task(created_task):
    """Проверяем, что задача создана корректно"""
    r = requests.get(f"{BASE_URL}/tasks/{created_task['id']}")
    assert r.status_code == 200
    assert r.json() == created_task


def test_delete_task(created_task):
    """Удаляем задачу и проверяем, что она удалена"""
    r = requests.delete(f"{BASE_URL}/tasks/{created_task['id']}")
    assert r.status_code == 200, f"Ошибка удаления задачи: {r.text}"

    # Проверка, что задача больше не существует
    r_check = requests.get(f"{BASE_URL}/tasks/{created_task['id']}")
    assert r_check.status_code == 404, f"Задача не удалена: {r_check.text}"


def test_task_not_found_after_delete(created_task):
    """Проверяем, что после удаления задача недоступна"""
    requests.delete(f"{BASE_URL}/tasks/{created_task['id']}")
    r = requests.get(f"{BASE_URL}/tasks/{created_task['id']}")
    assert r.status_code == 404, f"Удалённая задача всё ещё существует: {r.text}"