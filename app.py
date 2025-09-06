import os
import time
import uuid
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, request, jsonify, g

app = Flask(__name__)

# --- Logging con rotación ---
os.makedirs('logs', exist_ok=True)
formatter = logging.Formatter('%(asctime)s %(levelname)s [%(request_id)s] %(message)s')

class RequestIdFilter(logging.Filter):
    def filter(self, record):
        record.request_id = getattr(g, 'request_id', '-')
        return True

file_handler = RotatingFileHandler('logs/app.log', maxBytes=1_000_000, backupCount=3, encoding='utf-8')
file_handler.setFormatter(formatter)
file_handler.addFilter(RequestIdFilter())

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
console_handler.addFilter(RequestIdFilter())

app.logger.setLevel(logging.INFO)
app.logger.addHandler(file_handler)
app.logger.addHandler(console_handler)

@app.before_request
def add_request_id():
    g.request_id = uuid.uuid4().hex[:8]
    app.logger.info(f'{request.method} {request.path} from {request.remote_addr}')

@app.after_request
def log_response(resp):
    app.logger.info(f'{request.method} {request.path} -> {resp.status_code}')
    return resp

# --- Endpoints ---
@app.get("/")
def home():
    return "Hola, Flask está vivo."

@app.get("/health")
def health():
    return jsonify(status="ok", ts=int(time.time()))

@app.post("/bot")
def bot():
    if not request.is_json:
        return jsonify(error="expected application/json"), 400
    data = request.get_json(silent=True) or {}
    msg = (data.get("message") or "").strip()
    user_id = data.get("user_id")
    if not msg:
        return jsonify(error="message is required"), 400
    reply = f"Recibido: {msg}"
    app.logger.info(f'user_id={user_id} message="{msg}" reply="{reply}"')
    return jsonify(reply=reply, request_id=g.request_id)

# --- Extra: meta y favicon ---
start_time = time.time()

@app.get("/favicon.ico")
def favicon():
    return ("", 204)

@app.get("/meta.json")
def meta():
    uptime = int(time.time() - start_time)
    return jsonify(app="callcenter-ia", status="ok", uptime=uptime)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
