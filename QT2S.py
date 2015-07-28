__author__ = 'sofiane'

import redis
import json
import logging
import multiprocessing

from TwitterCollector import TwitterCollector
from TwitterClassifier import TwitterClassifier
from TwitterLocationER import TwitterLocationER

REDIS_NAMESPACE = 'QMIC'
REDIS_NAME_RAW_TWEETS = 'raw_tweets'
REDIS_NAME_TRAFFIC_TWEETS = 'traffic_tweets'
REDIS_NAME_GEOCODED_TWEETS = 'geocoded_tweets'
REDIS_DB = redis.Redis()


KEYWORD_DICT_FILE = 'data/traffic_dict.csv'
LOCATION_DICT_FILE = 'data/location_dict.csv'
SLANG_DICT_FILE = 'data/slang_dict.csv'


# Initialize the logger
# TODO: turn logging level to INFO before deploying into production.
logging.basicConfig(filename='/tmp/qmic.log',
			format = '%(levelname)s: %(module)s: %(funcName)s: %(message)s',
			level=logging.DEBUG)
logger = logging.getLogger('__name__')

def collect_tweets():
	"""
	Collect tweets matching input keywords in KEYWORD_DICT_FILE
	:return: writes into Redis Channel: REDIS_NAMESPACE:REDIS_NAME_RAW_TWEETS
	"""
	twitter_collector = TwitterCollector(r_db=REDIS_DB, r_channel='%s:%s' % (REDIS_NAMESPACE, REDIS_NAME_RAW_TWEETS),
										keyword_dict_file=KEYWORD_DICT_FILE)
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
	:return: writes into write channel
	"""
	read_channel = '%s:%s' % (REDIS_NAMESPACE, REDIS_NAME_TRAFFIC_TWEETS)
	write_channel = '%s:%s' % (REDIS_NAMESPACE, REDIS_NAME_GEOCODED_TWEETS)
	twitter_location_er = TwitterLocationER(location_dictionary_file=LOCATION_DICT_FILE, slang_dictionary_file=SLANG_DICT_FILE)
	while True:
		# read from Redis channel: REDIS_NAMESPACE:REDIS_NAME_RAW_TWEETS
		data = REDIS_DB.blpop(read_channel)
		if len(data) != 2:
			continue
		data = data[1]
		data = json.loads(data)
		locations = twitter_location_er.find_locations(data['text'])
		bad_words = twitter_location_er.contains_bad_words(data['text'])
		if len(locations) > 0:
			data['traffic_locations'] = list(locations)
			data['bad_words'] = list(bad_words)
			data['contains_bad_words'] = True if len(bad_words) > 0 else False
			# Write to a new Redis channel: REDIS_NAMESPACE:REDIS_NAME_TRAFFIC_TWEETS
			REDIS_DB.rpush(write_channel, json.dumps(data))

if __name__ == '__main__':
	collector = multiprocessing.Process(name='Collector', target=collect_tweets)
	collector.start()

	classifier = multiprocessing.Process(name='Classifier', target=classify_tweets)
	classifier.start()

	location_tagger = multiprocessing.Process(name='LocationER', target=extract_entities)
	location_tagger.start()

