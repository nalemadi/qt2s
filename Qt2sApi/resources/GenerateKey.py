__author__ = 'sofiane'

from flask_restful import Resource, abort, reqparse
from common.database import db
from common.models import Client


class GenerateKey(Resource):
	def get(self):
		parser = reqparse.RequestParser()
		parser.add_argument('name', type=str)
		parser.add_argument('key', type=str)
		args = parser.parse_args()
		name = args['name']
		if name is None:
			abort(400, message="missing argument")
		elif Client.query.filter_by(name=name).first() is not None:
			abort(400, message="user {} already exists".format(name))
		client = Client(name=name)
		client.generate_key()
		db.session.add(client)
		db.session.commit()
		return {'name': client.name, 'key': client.key}, 201

	def post(self):
		parser = reqparse.RequestParser()
		parser.add_argument('name', type=str)
		parser.add_argument('key', type=str)
		args = parser.parse_args()
		name = args['name']
		if name is None:
			abort(400, message="missing argument")
		elif Client.query.filter_by(name=name).first() is not None:
			abort(400, message="user {} already exists".format(name))
		client = Client(name=name)
		client.generate_key()
		db.session.add(client)
		db.session.commit()
		return {'name': client.name, 'key': client.key}, 201