__author__ = 'sofiane'

import json
import redis
import yaml

from flask_restful import fields, Resource, marshal_with, reqparse


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


class tweet_coordinates(fields.Raw):
	def output(self, key, obj):
		if obj['coordinates']:
			return {'lat': obj['coordinates']['coordinates'][0], 'lng': obj['coordinates']['coordinates'][0]}
		else:
			return None


class geocoded_locations(fields.Raw):
	def output(self, key, obj):
		return obj['traffic_locations']

# TODO: check what's wrong with using the fields to extract geocoded locations.
# location_fields = {
# 	'formatted_address': fields.String(default=None),
# 	'lat': fields.Float(default=None),
# 	'lng': fields.Float(default=None)
# }
#
# all_coordinates = {
# 	'google': fields.Nested(location_fields, default=None),
# 	'bing': fields.Nested(location_fields, default=None),
# 	'nominatim': fields.Nested(location_fields, default=None)
# }
#
# location_geocodes_fields = {
# 	'name': fields.String,
# 	'coordinates': fields.Nested(all_coordinates, default=None)
# }

tweet_fields = {
	'tweet_id': fields.String(attribute='id_str'),
	'tweet_text': fields.String(attribute='text'),
	'tweet_timestamp': fields.String(attribute='created_at'),
	'tweet_language': fields.String(attribute='lang'),
	'tweet_coordinates': tweet_coordinates,
	'user_id': user_id_str,
	'user_name': user_name,
	'user_screen_name': user_screen_name,
	'user_url_picture': user_url_picture,
	'contains_bad_words': fields.Boolean(default=False),
	'bad_words': fields.List(fields.String),
	'is_about_traffic': fields.Boolean(attribute='is_about_traffic'),
	'contains_traffic_locations': fields.Boolean(attribute='contains_traffic_locations', default=False),
	'traffic_locations': geocoded_locations
	# 'traffic_locations': fields.List(fields.Nested(location_geocodes_fields), default=None)
}


class TrafficTweets(Resource):
	def __init__(self):
		self.parser = reqparse.RequestParser()
		self.parser.add_argument('count', type=int, help='count cannot be converted')
		self.parser.add_argument('timestamp')
		self.parser.add_argument('languages', action='append')
		self.parser.add_argument('areas')
		with open("resources/apiconfig.yml",'r') as f:
			cfg = yaml.load(f)
		redis_host = cfg['redis']['host']
		redis_port = cfg['redis']['port']
		redis_hostname = cfg['redis']['hostname']
		redis_located_channel = cfg['redis']['channels']['located_tweets']
		self.redis_db = redis.Redis(host=redis_host, port=redis_port)
		self.redis_located_tweets_channel = '{0}:{1}'.format(redis_hostname,redis_located_channel)

	@marshal_with(tweet_fields)
	def get(self):
		args = self.parser.parse_args()
		count = args['count']
		tweets = self._get_tweets(count)
		return tweets, 200

	def _get_tweets(self, count):
		""" retrieve a list of tweets
		:rtype : list of tweets
		"""
		tweets = [json.loads(tw) for tw in self.redis_db.lrange(self.redis_located_tweets_channel, -count, -1)]
		return tweets
