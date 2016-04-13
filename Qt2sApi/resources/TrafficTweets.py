__author__ = 'sofiane'

import json
import yaml
import time
from datetime import datetime

from timeAnalyzer import *
from dataAnalyzer import *
from geoAnalyzer import *

from pymongo import MongoClient, errors

from flask_restful import fields, Resource, marshal_with, reqparse, abort
from common.models import Client

from config import *

try:
	connection = MongoClient(MONGODB_HOST, MONGODB_PORT, connect=False)
	print "<DEBUG>: Connected to MongoDB successfully!!!"


	COLLECTION_AR_NON_TRAFFIC = connection[DBS_NAME][COLLECTION_AR_NON_TRAFFIC_NAME]
	COLLECTION_ENG_NON_TRAFFIC = connection[DBS_NAME][COLLECTION_ENG_NON_TRAFFIC_NAME]

	COLLECTION_AR_NON_LOCATED_TRAFFIC = connection[DBS_NAME][COLLECTION_AR_NON_LOCATED_TRAFFIC_NAME]
	COLLECTION_ENG_NON_LOCATED_TRAFFIC = connection[DBS_NAME][COLLECTION_ENG_NON_LOCATED_TRAFFIC_NAME]

	COLLECTION_ENG_LOCATED_TRAFFIC_QA = connection[DBS_NAME][COLLECTION_ENG_LOCATED_TRAFFIC_QA_NAME]
	COLLECTION_AR_LOCATED_TRAFFIC_QA = connection[DBS_NAME][COLLECTION_AR_LOCATED_TRAFFIC_QA_NAME]

	COLLECTION_ENG_LOCATED_TRAFFIC_WORLDWIDE = connection[DBS_NAME][COLLECTION_ENG_LOCATED_TRAFFIC_WORLDWIDE_NAME]
	#COLLECTION_AR_LOCATED_TRAFFIC_WORLDWIDE = connection[DBS_NAME][COLLECTION_AR_LOCATED_TRAFFIC_WORLDWIDE_NAME]

except errors.ConnectionFailure, e:
   print "Could not connect to MongoDB: %s" % e


timeanalyzer = TimeAnalyzer()
dataanalyzer = DataAnalyzer()
geoAnalyzer = GeoAnalyzer()



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
		return None #obj['traffic_locations']


# releavant fields 
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
	'traffic_locations': geocoded_locations,
	'category': fields.String(attribute='category')
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

	def get(self):
		args = self.parser.parse_args()
		count = args['count']
		key = args['key']
		language = args['language']
		query = args['filter']

		if language == 'en':
			mongo_collection = COLLECTION_ENG_LOCATED_TRAFFIC_QA
		elif language == 'ar':
			mongo_collection = COLLECTION_AR_LOCATED_TRAFFIC_QA

		if not self.verify_key(key):
			abort(401, message="Unauthorized user")

		if query:
			# Consider a query in the format: [u'[keyword1,keyword2,keyword3,...]']
			query = [w.strip() for w in query[0].split(',')]
			tweets = self._get_filtered_tweets(mongo_collection, query, count)
		else:
			tweets = list(self._get_tweets(mongo_collection, count) )

		output = dict()
		output['res'] = tweets
		output['nb_tweets'] = len(tweets)
		# API Monitoring: insert into Redis
		# log_entry = dict()
		# log_entry['timestamp'] = time.strftime("%Y-%m-%d %H:%M:%S")
		# log_entry['params'] = dict()
		# log_entry['params']['count'] = count
		# client = Client.query.filter_by(key=key).first()
		# client_name = client.name
		# self.redis_db.rpush('QT2S:{}'.format(client_name), json.dumps(log_entry))
		# End API monitoring
		return output, 200



	@marshal_with(tweet_fields)
	def _get_tweets(self,collection,  count):
		""" Add comments later 
		"""
		data = dataanalyzer.get_last_nitems(collection, count)
		return data

	@marshal_with(tweet_fields)
	def _get_filtered_tweets(self, collection, keyword, count):
		"""
		Retrieves all the tweets that match one of the keywords in query
		:param query: list of keywords
		:return: list of tweets
		"""
		data = dataanalyzer.get_tweets_by_keyword(collection , keyword,count)
		return data


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

			mongo_collection = COLLECTION_ENG_LOCATED_TRAFFIC_QA
		elif language == 'ar':
			mongo_collection = COLLECTION_AR_LOCATED_TRAFFIC_QA

		if fromts and tots:
			tweets = self._get_filtered_tweets_from_to(mongo_collection, query, fromts, tots)
		elif since:
			tweets = self._get_filtered_tweets_since(mongo_collection , query, since)
		else:
			tweets = self._get_filtered_tweets(mongo_collection , query)

		output = dict()
		output['res'] = tweets
		output['nb_tweets'] = len(tweets)
		# API Monitoring: insert into Redis
		# log_entry = dict()
		# log_entry['timestamp'] = time.strftime("%Y-%m-%d %H:%M:%S")
		# log_entry['params'] = dict()
		# log_entry['params']['from'] = fromts
		# log_entry['params']['to'] = tots
		# client = Client.query.filter_by(key=key).first()
		# client_name = client.name
		# self.redis_db.rpush('QT2S:{}'.format(client_name), json.dumps(log_entry))
		# End API monitoring
		return output, 200


	@marshal_with(tweet_fields)
	def _get_filtered_tweets(self,collection,  query):
		"""
		Retrieves all the tweets that match one of the keywords in query
		:param query: list of keywords
		:return: list of tweets
		"""
		tweets = dataanalyzer.find_tweets_by_keywords(collection, query)
		return tweets

	@marshal_with(tweet_fields)
	def _get_filtered_tweets_since(self,collection,  query, since):
		"""
		Retrieves all the tweets posted after "since" that match one of the keywords in query
		:param query: list of keywords
		:return: list of tweets
		"""
		tweets = timeanalyzer.find_since_dt(collection, query,since)

		return tweets

	@marshal_with(tweet_fields)
	def _get_filtered_tweets_from_to(self,collection,  query, fromts, tots):
		"""
		Retrieves all the tweets that match one of the keywords in query, and that are posted in
		the interval [fromts, tots].
		:param query: list of keywords
		:return: list of tweets
		"""
		tweets = timeanalyzer.find_from_to(collection,  query, fromts, tots)

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

	# @staticmethod
	# def tweet_in_interval(tweet, fromts, tots):
	# 	ts = datetime.fromtimestamp(int(tweet['timestamp_ms']) / 1000).strftime('%Y-%m-%d %H:%M')
	# 	if ts >= fromts and ts <= tots:
	# 		return True
	# 	return False
