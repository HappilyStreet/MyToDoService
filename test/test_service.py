import requests

BASE_URL = "http://82.117.87.172:30181"

# Счётчик для уникальных числовых ID
task_counter = 1000

def generate_unique_id():
    """Генерация уникального целочисленного ID"""
    global task_counter
    task_counter += 1
    return task_counter


def test_create_task():
    """Создаём задачу и проверяем, что она верно возвращается"""
    task_id = generate_unique_id()
    payload = {
        "id": task_id,
        "title": "Smoke Test Task",
        "completed": False
    }
    r = requests.post(f"{BASE_URL}/tasks", json=payload)
    assert r.status_code == 200, f"Ошибка создания задачи: {r.text}"

    data = r.json()
    assert data["id"] == task_id
    assert data["title"] == "Smoke Test Task"
    assert data["completed"] is False

    return task_id


def test_delete_task():
    """Удаляем задачу, созданную выше"""
    task_id = test_create_task()  # создаём задачу перед удалением
    r = requests.delete(f"{BASE_URL}/tasks/{task_id}")
    assert r.status_code == 200, f"Ошибка удаления задачи: {r.text}"

    # Проверим, что задача больше не существует
    r_check = requests.get(f"{BASE_URL}/tasks/{task_id}")
    assert r_check.status_code == 404, f"Задача не удалена: {r_check.text}"


def test_task_not_found_after_delete():
    """Проверяем, что удалённая задача больше не существует"""
    task_id = test_create_task()
    requests.delete(f"{BASE_URL}/tasks/{task_id}")
    r = requests.get(f"{BASE_URL}/tasks/{task_id}")
    assert r.status_code == 404, f"Удалённая задача всё ещё существует: {r.text}"


def test_get_all_tasks():
    """Проверяем получение всех задач"""
    r = requests.get(f"{BASE_URL}/tasks")
    assert r.status_code == 200, f"Ошибка получения списка задач: {r.text}"
    assert isinstance(r.json(), list), "Ожидается список задач"