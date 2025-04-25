from functools import wraps
from flask import jsonify

def handle_exceptions(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            return jsonify({
                "error": "Error interno en el servidor",
                "error_detail": str(e)
            }), 500
    return wrapper
