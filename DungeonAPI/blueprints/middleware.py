from functools import wraps
from flask import jsonify, request

def admin_only(func):
    """
    route decorater to check if the user is an admin for restriced routes.

    Use as a decorator:
    `@admin_only`
    """
    @wraps(func)
    def handler(*args, **kwargs):

        is_admin = request.headers.get("Admin", None)
        if is_admin is None:
            return jsonify({'error': 'Please supply Authorization'}), 400
        if is_admin != "True":
            return jsonify({'error': 'You are not Authorized'}), 401

        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(e)
            return jsonify({'error': 'Internal Servor Error'}), 500
    return handler
