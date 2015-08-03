__author__ = 'sofiane'

from flask import Flask
from flask_restful import Api

from Qt2sApi.resources.traffictweets import TrafficTweets

app = Flask(__name__)
api = Api(app)

api.add_resource(TrafficTweets, '/qt2s', endpoint="tweets")

if __name__ == '__main__':
	app.run(debug=True)

