import time, uuid
from flask import Blueprint, request, jsonify, g, current_app
from app.utils.responses import success

bp = Blueprint('core', __name__)
start_time = time.time()

@bp.before_app_request
def add_request_id():
    g.request_id = uuid.uuid4().hex[:8]
    current_app.logger.info(f'{request.method} {request.path} from {request.remote_addr}')

@bp.after_app_request
def log_response(resp):
    current_app.logger.info(f'{request.method} {request.path} -> {resp.status_code}')
    return resp

@bp.get('/')
def home():
    return 'Hola, Flask está vivo.'

@bp.get('/health')
def health():
    return jsonify(status='ok', ts=int(time.time()))

@bp.post('/bot')
def bot():
    if not request.is_json:
        return jsonify(error='expected application/json'), 400
    data = request.get_json(silent=True) or {}
    msg = (data.get('message') or '').strip()
    user_id = data.get('user_id')
    if not msg:
        return jsonify(error='message is required'), 400
    reply = f'Recibido: {msg}'
    current_app.logger.info(f'user_id={user_id} message="{msg}" reply="{reply}"')
    return success({'reply': reply})

@bp.get('/favicon.ico')
def favicon():
    return ('', 204)

@bp.get('/meta.json')
def meta():
    uptime = int(time.time() - start_time)
    return jsonify(
        app=current_app.config.get('APP_NAME'),
        status='ok',
        env=current_app.config.get('ENV'),
        uptime=uptime
    )
