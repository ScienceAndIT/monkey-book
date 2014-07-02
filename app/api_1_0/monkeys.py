from flask import jsonify, request, current_app, url_for
from . import api
from ..models import Monkey


@api.route('/monkeys/<int:id>')
def get_monkey(id):
    monkey = Monkey.query.get_or_404(id)
    return jsonify(monkey.to_json())


@api.route('/monkeys/<int:id>/friends/')
def get_monkey_friends(id):
    pass

