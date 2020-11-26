import json

from flask import Flask, request, jsonify, make_response

from src.model import Discount
from src.redis_storage import init_redis_storage

app = Flask(__name__)

storage = init_redis_storage()


@app.route('/healthy', methods=['GET'])
def healthy():
    """The end-point for health check."""
    return "OK"


@app.route('/discount', methods=['POST'])
def create_discount():
    """Creates one or more discounts for a brand."""
    discount = Discount.from_json_str(request.data)
    stored_discount = storage.insert(discount)
    return jsonify(stored_discount.__dict__)


@app.route('/discount', methods=['GET'])
def list_discounts():
    """Returns all discounts"""
    out = storage.get_discounts()
    print(out)
    return jsonify(discounts=[o.__dict__ for o in out])


@app.route('/discount/<discount_id>/grant', methods=['POST'])
def grant_discount(discount_id: str):
    """Grant a particular discount to a user."""
    request_body = json.loads(request.data.decode('utf-8'))
    granted_discount_id = storage.grant(discount_id, request_body['user_id'])
    if not granted_discount_id:
        return make_response(jsonify(
            {"message": "Discount not found or not available any more."}), 404)
    return jsonify({"discount_id": granted_discount_id,
                    "granted": True})


if __name__ == '__main__':
    app.run('0.0.0.0', debug=True)
