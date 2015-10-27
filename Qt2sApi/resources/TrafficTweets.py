__author__ = 'sofiane'

import json
import redis
import yaml
import time
from datetime import datetime

from flask_restful import fields, Resource, marshal_with, reqparse, abort
from common.models import Client


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
			return {'lat': obj['coordinates']['coordinates'][1], 'lng': obj['coordinates']['coordinates'][0]}
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
}


class TrafficRecentTweets(Resource):
	def __init__(self):
		self.parser = reqparse.RequestParser()
		self.parser.add_argument('count', type=int, default=50, help='count cannot be converted')
		self.parser.add_argument('key', type=str, required=True, help='API Key')
		self.parser.add_argument('timestamp')
		self.parser.add_argument('language', default='en', type=str, help='provide language of tweets. example: ar/en')
		self.parser.add_argument('filter', action='append', help='query terms')
		self.parser.add_argument('areas')

		with open("resources/apiconfig.yml",'r') as f:
			cfg = yaml.load(f)
		redis_host = cfg['redis']['host']
		redis_port = cfg['redis']['port']
		redis_hostname = cfg['redis']['hostname']
		redis_located_en_channel = cfg['redis']['channels']['located_tweets']
		redis_located_ar_channel = cfg['redis']['channels']['located_arabic_traffic_tweets']
		self.redis_db = redis.Redis(host=redis_host, port=redis_port)
		self.redis_located_en_tweets_channel = '{0}:{1}'.format(redis_hostname,redis_located_en_channel)
		self.redis_located_ar_tweets_channel = '{0}:{1}'.format(redis_hostname,redis_located_ar_channel)

	def get(self):
		args = self.parser.parse_args()
		count = args['count']
		key = args['key']
		language = args['language']
		query = args['filter']

		if language == 'en':
			redis_channel = self.redis_located_en_tweets_channel
		elif language == 'ar':
			redis_channel = self.redis_located_ar_tweets_channel

		if not self.verify_key(key):
			abort(401, message="Unauthorized user")

		if query:
			# Consider a query in the format: [u'[keyword1,keyword2,keyword3,...]']
			query = [w.strip() for w in query[0].split(',')]
			tweets = self._get_filtered_tweets(query, redis_channel, count)
		else:
			tweets = self._get_tweets(redis_channel, count)

		output = dict()
		output['res'] = tweets
		output['nb_tweets'] = len(tweets)
		# API Monitoring: insert into Redis
		log_entry = dict()
		log_entry['timestamp'] = time.strftime("%Y-%m-%d %H:%M:%S")
		log_entry['params'] = dict()
		log_entry['params']['count'] = count
		client = Client.query.filter_by(key=key).first()
		client_name = client.name
		self.redis_db.rpush('QT2S:{}'.format(client_name), json.dumps(log_entry))
		# End API monitoring
		return output, 200

	@marshal_with(tweet_fields)
	def _get_tweets(self, redis_queue, count):
		""" retrieve a list of "count" tweets from the input redis_queue
		:rtype : list of tweets
		"""

		tweets = [json.loads(tw) for tw in self.redis_db.lrange(redis_queue, -count, -1)]
		return tweets

	@marshal_with(tweet_fields)
	def _get_filtered_tweets(self, query, redis_queue, count):
		"""
		Retrieves all the tweets that match one of the keywords in query
		:param query: list of keywords
		:return: list of tweets
		"""

		queue_len = self.redis_db.llen(redis_queue)
		tweets = []
		for i in reversed(range(queue_len)):
			tweet = self.redis_db.lindex(redis_queue, i)
			tweet = json.loads(tweet)
			for q in query:
				if q.lower() in tweet['text'].lower():
					tweets.append(tweet)
					break
			if len(tweets) == count:
				break
		return tweets

	@staticmethod
	def verify_key(key):
		""" Checks if the key exists in the database.
		:param key: the api key supplied by the user
		:return: True if key is valid, False otherwise.
		"""
		if not Client.query.filter_by(key=key).first():
			return False
		return True

class TrafficSearchTweets(Resource):
	def __init__(self):
		self.parser = reqparse.RequestParser()
		self.parser.add_argument('key', type=str, required=True, help='API Key')
		self.parser.add_argument('language', default='en', type=str, help='provide language of tweets. example: ar/en')
		self.parser.add_argument('q', action='append', required=True, help='query terms')
		self.parser.add_argument('from', type=str, help='tweets posted after this datetime: yyyy-mm-dd hh:mm')
		self.parser.add_argument('to', type=str, help='tweets posted before this datetime: yyyy-mm-dd hh:mm')
		self.parser.add_argument('since', type=str, help='tweets posted since this datetime: yyyy-mm-dd hh:mm')

		with open("resources/apiconfig.yml",'r') as f:
			cfg = yaml.load(f)
		redis_host = cfg['redis']['host']
		redis_port = cfg['redis']['port']
		redis_hostname = cfg['redis']['hostname']
		redis_located_en_channel = cfg['redis']['channels']['located_tweets']
		redis_located_ar_channel = cfg['redis']['channels']['located_arabic_traffic_tweets']
		self.redis_db = redis.Redis(host=redis_host, port=redis_port)
		self.redis_located_en_tweets_channel = '{0}:{1}'.format(redis_hostname,redis_located_en_channel)
		self.redis_located_ar_tweets_channel = '{0}:{1}'.format(redis_hostname,redis_located_ar_channel)

	def get(self):
		# Get the parameters
		args = self.parser.parse_args()
		key = args['key']
		language = args['language']
		query = args['q']
		fromts = args['from']
		tots = args['to']
		since = args['since']

		if not self.verify_key(key):
			abort(401, message="Unauthorized user")

		# Consider a query in the format: [u'[keyword1,keyword2,keyword3,...]']
		query = [w.strip() for w in query[0].split(',')]

		if language == 'en':
			redis_channel = self.redis_located_en_tweets_channel
		elif language == 'ar':
			redis_channel = self.redis_located_ar_tweets_channel

		if fromts and tots:
			tweets = self._get_filtered_tweets_from_to(query, redis_channel, fromts, tots)
		elif since:
			tweets = self._get_filtered_tweets_since(query, redis_channel, since)
		else:
			tweets = self._get_filtered_tweets(query, redis_channel)

		output = dict()
		output['res'] = tweets
		output['nb_tweets'] = len(tweets)
		# API Monitoring: insert into Redis
		log_entry = dict()
		log_entry['timestamp'] = time.strftime("%Y-%m-%d %H:%M:%S")
		log_entry['params'] = dict()
		log_entry['params']['from'] = fromts
		log_entry['params']['to'] = tots
		client = Client.query.filter_by(key=key).first()
		client_name = client.name
		self.redis_db.rpush('QT2S:{}'.format(client_name), json.dumps(log_entry))
		# End API monitoring
		return output, 200

	@marshal_with(tweet_fields)
	def _get_filtered_tweets(self, query, redis_queue):
		"""
		Retrieves all the tweets that match one of the keywords in query
		:param query: list of keywords
		:return: list of tweets
		"""

		queue_len = self.redis_db.llen(redis_queue)
		tweets = []
		for i in reversed(range(queue_len)):
			tweet = self.redis_db.lindex(redis_queue, i)
			tweet = json.loads(tweet)
			for q in query:
				if q.lower() in tweet['text'].lower():
					tweets.append(tweet)
					break
		return tweets

	@marshal_with(tweet_fields)
	def _get_filtered_tweets_since(self, query, redis_queue, since):
		"""
		Retrieves all the tweets posted after "since" that match one of the keywords in query
		:param query: list of keywords
		:return: list of tweets
		"""

		queue_len = self.redis_db.llen(redis_queue)
		tweets = []
		for i in reversed(range(queue_len)):
			tweet = self.redis_db.lindex(redis_queue, i)
			tweet = json.loads(tweet)
			ts = datetime.fromtimestamp(int(tweet['timestamp_ms']) / 1000).strftime('%Y-%m-%d %H:%M')
			# IMPORTANT: stop looking for tweets beyond the since limit
			if ts < since:
				break

			for q in query:
				if q.lower() in tweet['text'].lower():
					tweets.append(tweet)
					break
		return tweets

	@marshal_with(tweet_fields)
	def _get_filtered_tweets_from_to(self, query, redis_queue, fromts, tots):
		"""
		Retrieves all the tweets that match one of the keywords in query, and that are posted in
		the interval [fromts, tots].
		:param query: list of keywords
		:return: list of tweets
		"""

		queue_len = self.redis_db.llen(redis_queue)
		tweets = []
		for i in reversed(range(queue_len)):
			tweet = self.redis_db.lindex(redis_queue, i)
			tweet = json.loads(tweet)
			ts = datetime.fromtimestamp(int(tweet['timestamp_ms']) / 1000).strftime('%Y-%m-%d %H:%M')
			# IMPORTANT: stop looking for tweets beyond the from limit, and do not treat tweets after tots
			if ts < fromts:
				break
			elif ts > tots:
				continue

			for q in query:
				if q.lower() in tweet['text'].lower():
					tweets.append(tweet)
					break
		return tweets

	@staticmethod
	def verify_key(key):
		""" Checks if the key exists in the database.
		:param key: the api key supplied by the user
		:return: True if key is valid, False otherwise.
		"""
		if not Client.query.filter_by(key=key).first():
			return False
		return True

	@staticmethod
	def tweet_in_interval(tweet, fromts, tots):
		ts = datetime.fromtimestamp(int(tweet['timestamp_ms']) / 1000).strftime('%Y-%m-%d %H:%M')
		if ts >= fromts and ts <= tots:
			return True
		return False
