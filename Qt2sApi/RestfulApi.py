__author__ = 'sofiane'

import os

from flask import Flask
from flask_restful import Api
from resources.TrafficTweets import TrafficTweets
from resources.GenerateKey import GenerateKey
from Qt2sApi.common.database import db


app = Flask(__name__)

# This is the only way I could find to make sqlAlchemy work correctly.
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///qt2s.sqlite'
db.init_app(app)
with app.test_request_context():
	db.create_all()

api = Api(app)

api.add_resource(TrafficTweets, '/api/v1/tweets/recent', endpoint="tweets")
api.add_resource(GenerateKey, '/api/v1/access/generate_key', endpoint="keys")

if __name__ == '__main__':
	if not os.path.exists('qt2s.sqlite'):
		db.create_all()
	app.run(debug=True)

