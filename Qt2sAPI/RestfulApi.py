__author__ = 'sofiane'
import json
from flask import Flask, request
from flask_restful import Resource, Api, reqparse, fields, marshal_with

app = Flask(__name__)
api = Api(app)

todos = dict()

parser = reqparse.RequestParser()
parser.add_argument('count', type=int, help='count cannot be converted')
parser.add_argument('timestamp')
parser.add_argument('languages', action='append')
parser.add_argument('region')

class userid(fields.Raw):
	def output(self, key, obj):
		return obj['user']['name']


tweet_fields = {
	'tweet_id': fields.String(attribute='id_str'),
	'tweet_text': fields.String(attribute='text'),
	# 'tweet_timestamp': fields.DateTime(attribute='created_at'),
	'user_id': userid,
	# 'user_id': fields.String(attribute='user'.'id_str'),
	# 'user_name': fields.String,
	# 'user_screenname': fields.String,
	# 'user_url_picture': fields.String,
	# 'is_about_traffic': fields.Boolean,
	# 'contains_traffic_locations': fields.Boolean,
	# 'traffic_locations': fields.List
}





class Tweets(Resource):
	@marshal_with(tweet_fields)
	def get(self):
		args = parser.parse_args()
		print args
		tweets = get_tweets()
		return tweets

def get_tweets():
	# tweets = open('../data/tweets_sample.txt').read().split('\n')
	tweets = [json.loads(tw) for tw in open('../data/tweets_sample.txt').read().split('\n')]
	return tweets



# class Qt2sTweets(Resource):
# 	def get(self): pass
#
# 	def put(self): pass
#
#
# class TodoSimple(Resource):
# 	def get(self, todo_id):
# 		return {todo_id: todos[todo_id]}
#
# 	def put(self, todo_id):
# 		args = parser.parse_args()
# 		print args['task']
# 		todos[todo_id] = request.form['task']
# 		return {todo_id: todos[todo_id]}

api.add_resource(Tweets, '/qt2s', endpoint='todo_ep')

if __name__ == '__main__':
	app.run(debug=True)




