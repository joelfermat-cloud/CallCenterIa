from flask import jsonify, g

def success(data=None, **extra):
    payload = {"ok": True, "request_id": getattr(g, "request_id", "-")}
    if data is not None:
        payload["data"] = data
    if extra:
        payload.update(extra)
    return jsonify(payload), 200
