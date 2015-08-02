__author__ = 'sofiane'
from flask_restful import fields, Resource, marshal_with, reqparse
import json


class user_id_str(fields.Raw):
	def output(self, key, obj):
		return obj['user']['id_str']


class user_name(fields.Raw):
	def output(self, key, obj):
		return obj['user']['name']


class user_screen_name(fields.Raw):
	def output(self, key, obj):
		return obj['user']['screen_name']


class user_url_picture(fields.Raw):
	def output(self, key, obj):
		return obj['user']['profile_image_url']


tweet_fields = {
	'tweet_id': fields.String(attribute='id_str'),
	'tweet_text': fields.String(attribute='text'),
	'tweet_timestamp': fields.String(attribute='created_at'),
	'user_id': user_id_str,
	'user_name': user_name,
	'user_screen_name': user_screen_name,
	'user_url_picture': user_url_picture,
	'contains_bad_words': fields.Boolean(default=False),
	'bad_words': fields.List(fields.String),
	'is_about_traffic': fields.Boolean(attribute='is_about_traffic'),
	'contains_traffic_locations': fields.Boolean(attribute='contains_traffic_locations', default=False),
	'traffic_locations': fields.List(fields.String)
}


class TrafficTweets(Resource):
	def __init__(self):
		self.parser = reqparse.RequestParser()
		self.parser.add_argument('count', type=int, help='count cannot be converted')
		self.parser.add_argument('timestamp')
		self.parser.add_argument('languages', action='append')
		self.parser.add_argument('region')

	@marshal_with(tweet_fields)
	def get(self):
		args = self.parser.parse_args()
		count = args['count']
		tweets = self.get_tweets(count)
		return tweets, 200

	def get_tweets(self, count):
		""" retrieve a list of tweets

		:rtype : list of tweets
		"""
		tweets = [json.loads(tw) for tw in open('../data/tweets_sample.txt').read().split('\n')]
		return tweets[:count]
