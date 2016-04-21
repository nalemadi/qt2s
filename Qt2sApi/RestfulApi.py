__author__ = 'sofiane'

import os

from flask import Flask
from flask_restful import Api
from resources.TrafficTweets import TrafficRecentTweets, TrafficSearchTweets
from resources.GenerateKey import GenerateKey
from common.database import db

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///qt2s.sqlite'
db.init_app(app)
with app.test_request_context():
	db.create_all()

api = Api(app)
api.add_resource(TrafficRecentTweets, '/api/v1/tweets/recent', endpoint="recent_tweets")
api.add_resource(TrafficSearchTweets, '/api/v1/tweets/search', endpoint="matching_tweets")
api.add_resource(GenerateKey, '/api/v1/access/generate_key', endpoint="keys")

if __name__ == '__main__':
	if not os.path.exists('qt2s.sqlite'):
		db.create_all()
	#app.run(host="0.0.0.0",port=5005,debug=True)
	app.run(debug=True)