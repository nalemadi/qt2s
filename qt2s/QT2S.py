__author__ = 'sofiane'

import redis
import json
import logging
import multiprocessing

from TwitterCollector import TwitterCollector
from TwitterClassifier import TwitterClassifier
from TwitterLocationER import TwitterLocationER
from SlangDetection import SlangDetection
from geocoding.LocationGeocoding import LocationGeocoding
from datetime import datetime


REDIS_NAMESPACE = 'QMIC'
REDIS_NAME_RAW_TWEETS = 'raw_tweets'
REDIS_NAME_TRAFFIC_TWEETS = 'traffic_tweets'
REDIS_NAME_NON_LOCATED_TWEETS = 'non_traffic_tweets'
REDIS_NAME_LOCATED_TWEETS = 'located_tweets'
REDIS_DB = redis.Redis()


KEYWORD_DICT_FILE = 'data/traffic_dict.csv'
LOCATION_DICT_FILE = 'data/location_dict.csv'
GEOCODED_LOCATION_DICT_FILE = 'data/geolocated_locations.txt'
SLANG_DICT_FILE = 'data/slang_dict.csv'
CITIES_NAME = 'data/qatar_cities_dict.txt'

GOOGLE_KEY = '[REDACTED]'
BING_KEY = '[REDACTED]'


# Initialize the logger
# TODO: turn logging level to INFO before deploying into production.
logging.basicConfig(filename='/tmp/qmic.log',
			format='%(levelname)s: %(module)s: %(funcName)s: %(message)s',
			level=logging.INFO)
logger = logging.getLogger('__name__')

# just for testing

def collect_tweets():
	"""
	Collect tweets matching input keywords in KEYWORD_DICT_FILE
	:return: writes into Redis Channel: REDIS_NAMESPACE:REDIS_NAME_RAW_TWEETS
	"""
	write_channel = '%s:%s' % (REDIS_NAMESPACE, REDIS_NAME_RAW_TWEETS)
	twitter_collector = TwitterCollector(r_db=REDIS_DB, r_channel=write_channel,
										keyword_dict_file=KEYWORD_DICT_FILE)
	logger.info("Starting Collector. Will read from twitter and write into %s", write_channel)
	twitter_collector.get_tweets()


def classify_tweets():
	"""
	Reads from redis channel REDIS_NAMESPACE:REDIS_NAME_RAW_TWEETS, checks if the tweet is about traffic
	then write to the redis channel: REDIS_NAMESPACE:REDIS_NAME_TRAFFIC_TWEETS
	:return:
	"""
	read_channel = '%s:%s' % (REDIS_NAMESPACE, REDIS_NAME_RAW_TWEETS)
	write_channel = '%s:%s' % (REDIS_NAMESPACE, REDIS_NAME_TRAFFIC_TWEETS)
	tweet_classifier = TwitterClassifier(method='Keyword', keyword_dictionary_file=KEYWORD_DICT_FILE)
	logger.info("Starting Classifier. Will read from %s and write into %s", read_channel, write_channel)
	while True:
		# read from Redis channel: REDIS_NAMESPACE:REDIS_NAME_RAW_TWEETS
		data = REDIS_DB.blpop(read_channel)
		if len(data) != 2:
			continue
		data = data[1]
		logger.debug("READ from redis [type:%s]: %s", type(data), data)
		data = json.loads(data)
		if tweet_classifier.is_about_traffic(data):
			data['is_about_traffic'] = True
			# Write to a new Redis channel: REDIS_NAMESPACE:REDIS_NAME_TRAFFIC_TWEETS
			REDIS_DB.rpush(write_channel, json.dumps(data))


def extract_entities():
	"""
	Extract location from tweets. Blocking reads from read_channel,
	extract locations, then writes into write channel
	!! This also checks for the presence of bad words in the tweet text
	:return: writes into write channel
	"""
	read_channel = '%s:%s' % (REDIS_NAMESPACE, REDIS_NAME_TRAFFIC_TWEETS)
	write_channel = '%s:%s' % (REDIS_NAMESPACE, REDIS_NAME_LOCATED_TWEETS)
	non_located_channel = '%s:%s' % (REDIS_NAMESPACE, REDIS_NAME_NON_LOCATED_TWEETS)

	twitter_location_er = TwitterLocationER(location_dictionary_file=LOCATION_DICT_FILE, cities_name=CITIES_NAME)
	slang_detection = SlangDetection(slang_dictionary_file=SLANG_DICT_FILE)
	location_geocoding = LocationGeocoding(google_key=GOOGLE_KEY, bing_key=BING_KEY, country_code='QA', geocoded_location_file=GEOCODED_LOCATION_DICT_FILE)
	logger.info("Starting LocationTagger. Will read from %s and write into %s", read_channel, write_channel)

	while True:
		# read from Redis channel: REDIS_NAMESPACE:REDIS_NAME_RAW_TWEETS
		data = REDIS_DB.blpop(read_channel)
		if len(data) != 2:
			continue
		data = data[1]
		data = json.loads(data)
		locations = twitter_location_er.find_locations(data['text'])
		# TODO: geo code the locations.
		# TODO: check if the locations have been geocoded in the past before sending online requests.

		bad_words = slang_detection.contains_bad_words(data['text'])
		# Remove a trivial false positive: Pearl Jam
		if len(locations) > 0 and 'pearl jam' not in data['text'].lower():
			geocoded_locations = [location_geocoding.geocode_location(location) for location in locations]
			data['traffic_locations'] = geocoded_locations
			data['bad_words'] = list(bad_words)
			data['contains_bad_words'] = True if len(bad_words) > 0 else False
			# Write to a new Redis channel: REDIS_NAMESPACE:REDIS_NAME_TRAFFIC_TWEETS
			REDIS_DB.rpush(write_channel, json.dumps(data))
			logger.info("New located tweets:%s\n Locations: %s", data['text'], list(locations))
		else:
			# add the tweet to the end, and make sure the list has at most 100K tweets
			REDIS_DB.rpush(non_located_channel, json.dumps(data))
			REDIS_DB.ltrim(non_located_channel, -100000, -1)

if __name__ == '__main__':
	logger.info('\n\n=================\n\nNEW INSTANCE\n-------------\n-->Started on: %s\n',datetime.now())
	collector = multiprocessing.Process(name='Collector', target=collect_tweets)
	collector.start()

	classifier = multiprocessing.Process(name='Classifier', target=classify_tweets)
	classifier.start()

	location_tagger = multiprocessing.Process(name='LocationER', target=extract_entities)
	location_tagger.start()

