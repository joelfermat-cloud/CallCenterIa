import uuid
from flask import Blueprint, request, jsonify, g, current_app
from app.utils.responses import success

bp = Blueprint('api_v1', __name__)

def _route_message(text: str) -> dict:
    t = (text or '').lower()
    if any(k in t for k in ['agente', 'humano', 'operador']):
        return {'action': 'handoff', 'reason': 'user_requested_agent'}
    return {'action': 'answer', 'reason': 'auto_reply'}

@bp.post('/echo')
def echo_v1():
    if not request.is_json:
        return jsonify(error='expected application/json'), 400
    data = request.get_json(silent=True) or {}
    return success({'echo': data.get('message'), 'meta': data.get('meta') or {}})

@bp.post('/messages')
def messages_v1():
    if not request.is_json:
        return jsonify(error='expected application/json'), 400
    data = request.get_json(silent=True) or {}
    msg = (data.get('message') or '').strip()
    user_id = data.get('user_id') or 'anon'

    if not msg:
        return jsonify(error='message is required'), 400

    route = _route_message(msg)
    if route['action'] == 'answer':
        reply = f'Recibido: {msg}'
    else:
        reply = 'Te paso con un agente humano.'

    current_app.logger.info(f'user_id={user_id} route="{route}" msg="{msg}" reply="{reply}"')
    return success({'reply': reply, 'route': route})
