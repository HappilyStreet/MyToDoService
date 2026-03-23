from flask import Flask, request, jsonify
from prometheus_client import CollectorRegistry, Counter, push_to_gateway
import threading

# ---------------------------
# Flask приложение
# ---------------------------
app = Flask(__name__)

# ---------------------------
# Prometheus Pushgateway метрики
# ---------------------------
registry = CollectorRegistry()

# Счётчик HTTP-запросов
HTTP_REQUESTS = Counter(
    'http_requests_total',        # имя метрики
    'Total HTTP requests',        # описание
    ['method', 'endpoint', 'status'],  # лейблы: метод, путь, статус
    registry=registry
)

PUSHGATEWAY_ADDRESS = 'pushgateway:9091'  # адрес Pushgateway в кластере
JOB_NAME = 'mytodoservice'

# ---------------------------
# После каждого запроса пушим метрику
# ---------------------------
@app.after_request
def after_request(response):
    HTTP_REQUESTS.labels(
        method=request.method,
        endpoint=request.path,
        status=response.status_code
    ).inc()

    # Отправляем метрики в Pushgateway
    push_to_gateway(PUSHGATEWAY_ADDRESS, job=JOB_NAME, registry=registry)

    return response

# ---------------------------
# Пример API
# ---------------------------
todos = []

@app.route("/tasks", methods=["GET"])
def get_tasks():
    return jsonify(todos), 200

@app.route("/tasks", methods=["POST"])
def add_task():
    data = request.get_json()
    todos.append(data)
    return jsonify(data), 201

@app.route("/tasks/<int:index>", methods=["DELETE"])
def delete_task(index):
    if 0 <= index < len(todos):
        task = todos.pop(index)
        return jsonify(task), 200
    return jsonify({"error": "Not found"}), 404

# ---------------------------
# Запуск сервера
# ---------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)