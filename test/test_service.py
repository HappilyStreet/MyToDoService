import pytest
import requests

BASE_URL = "http://82.117.87.172:30181"

@pytest.fixture
def created_task():
    """Создаём задачу перед тестами"""
    data = {"title": "Smoke Test Task"}
    r = requests.post(f"{BASE_URL}/tasks/", json=data)
    assert r.status_code == 200
    return r.json()

def test_create_task(created_task):
    """Проверяем, что задача создана корректно"""
    r = requests.get(f"{BASE_URL}/tasks/{created_task['id']}")
    assert r.status_code == 200
    assert r.json()["title"] == "Smoke Test Task"

def test_delete_task(created_task):
    """Удаляем задачу и проверяем, что она удалена"""
    r = requests.delete(f"{BASE_URL}/tasks/{created_task['id']}")
    assert r.status_code == 200

    # Проверка, что задача больше не существует
    r_check = requests.get(f"{BASE_URL}/tasks/{created_task['id']}")
    assert r_check.status_code == 404

def test_task_not_found_after_delete(created_task):
    """Проверяем, что после удаления задача недоступна"""
    requests.delete(f"{BASE_URL}/tasks/{created_task['id']}")
    r = requests.get(f"{BASE_URL}/tasks/{created_task['id']}")
    assert r.status_code == 404