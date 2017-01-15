__author__ = 'sofiane'

import json
import logging
import multiprocessing
import subprocess
import os
from datetime import datetime
import yaml
from pymongo import MongoClient, errors
import redis

from collector.TwitterCollector import TwitterCollector
from traffic_classifier.TwitterClassifier import TwitterClassifier
from location_recognition.TwitterLocationER import TwitterLocationER
from persister.TwitterPersister import TwitterPersister
from resources.SlangDetection import SlangDetection
from geocoding.LocationGeocoding import LocationGeocoding
from traffic_classifier.ArabicTwitterClassifier import ArabicTwitterClassifier
from location_recognition.ArabicTwitterLocationER import ArabicTwitterLocationER
from incident_classifier.IncidentClassifier import IncidentClassifier
from resources.resources import has_black_listed_location
from resources.resources import has_ar_blacklisted_location


from resources.mongodb_config import *

# ---------------------------------
# Configuration File
# ---------------------------------
with open("resources/qt2sconfig.yml", 'r') as f:
	cfg = yaml.load(f)


# -------------------- #
# MongoDB Connection
# -------------------- #
MONGODB_HOST = cfg['mongodb']['hostname']
MONGODB_PORT = cfg['mongodb']['port']
DBS_NAME = cfg['mongodb']['dbname']
COLLECTION_AR_NON_TRAFFIC_NAME = cfg['mongodb']['collections']['COLLECTION_AR_NON_TRAFFIC_NAME']
COLLECTION_ENG_NON_TRAFFIC_NAME = cfg['mongodb']['collections']['COLLECTION_ENG_NON_TRAFFIC_NAME']
COLLECTION_AR_NON_LOCATED_TRAFFIC_NAME = cfg['mongodb']['collections']['COLLECTION_AR_NON_LOCATED_TRAFFIC_NAME']
COLLECTION_ENG_NON_LOCATED_TRAFFIC_NAME = cfg['mongodb']['collections']['COLLECTION_ENG_NON_LOCATED_TRAFFIC_NAME']
COLLECTION_ENG_LOCATED_TRAFFIC_QA_NAME = cfg['mongodb']['collections']['COLLECTION_ENG_LOCATED_TRAFFIC_QA_NAME']
COLLECTION_AR_LOCATED_TRAFFIC_QA_NAME = cfg['mongodb']['collections']['COLLECTION_AR_LOCATED_TRAFFIC_QA_NAME']
COLLECTION_ENG_LOCATED_TRAFFIC_WORLDWIDE_NAME = cfg['mongodb']['collections']['COLLECTION_ENG_LOCATED_TRAFFIC_WORLDWIDE_NAME']

connection = MongoClient(MONGODB_HOST, MONGODB_PORT, connect=False)
COLLECTION_AR_NON_TRAFFIC = connection[DBS_NAME][COLLECTION_AR_NON_TRAFFIC_NAME]
COLLECTION_ENG_NON_TRAFFIC = connection[DBS_NAME][COLLECTION_ENG_NON_TRAFFIC_NAME]
COLLECTION_AR_NON_LOCATED_TRAFFIC = connection[DBS_NAME][COLLECTION_AR_NON_LOCATED_TRAFFIC_NAME]
COLLECTION_ENG_NON_LOCATED_TRAFFIC = connection[DBS_NAME][COLLECTION_ENG_NON_LOCATED_TRAFFIC_NAME]
COLLECTION_ENG_LOCATED_TRAFFIC_QA = connection[DBS_NAME][COLLECTION_ENG_LOCATED_TRAFFIC_QA_NAME]
COLLECTION_AR_LOCATED_TRAFFIC_QA = connection[DBS_NAME][COLLECTION_AR_LOCATED_TRAFFIC_QA_NAME]
COLLECTION_ENG_LOCATED_TRAFFIC_WORLDWIDE = connection[DBS_NAME][COLLECTION_ENG_LOCATED_TRAFFIC_WORLDWIDE_NAME]


# ---------------------------------
# Redis Configuration
# ---------------------------------

REDIS_NAMESPACE = cfg['redis']['hostname']
REDIS_NAME_RAW_TWEETS = cfg['redis']['channels']['raw_tweets']
REDIS_NAME_TRAFFIC_TWEETS = cfg['redis']['channels']['traffic_tweets']
REDIS_NAME_NON_TRAFFIC_TWEETS = cfg['redis']['channels']['non_traffic_tweets']
REDIS_NAME_LOCATED_TRAFFIC_TWEETS = cfg['redis']['channels']['located_traffic_tweets']
REDIS_NAME_NON_LOCATED_TRAFFIC_TWEETS = cfg['redis']['channels']['non_located_traffic_tweets']
REDIS_NAME_RAW_ARABIC_TWEETS = cfg['redis']['channels']['raw_arabic_tweets']
REDIS_NAME_NON_TRAFFIC_ARABIC_TWEETS = cfg['redis']['channels']['non_traffic_arabic_tweets']
REDIS_NAME_TRAFFIC_ARABIC_TWEETS = cfg['redis']['channels']['traffic_arabic_tweets']
REDIS_NAME_NON_LOCATED_ARABIC_TRAFFIC_TWEETS = cfg['redis']['channels']['non_located_arabic_traffic_tweets']
REDIS_NAME_LOCATED_ARABIC_TRAFFIC_TWEETS = cfg['redis']['channels']['located_arabic_traffic_tweets']
REDIS_NAME_WORLDWIDE_GEOLOCATED_TWEETS = cfg['redis']['channels']['worldwide_geolocated_tweets']
REDIS_DB = redis.Redis(host=cfg['redis']['host'], port=cfg['redis']['port'])

KEYWORD_DICT_FILE = 'data/traffic_dict.csv'
GEOCODED_LOCATION_DICT_FILE = 'data/geolocated_locations.txt'
GEOCODED_LOCATION_AR_DICT_FILE = 'data/geolocated_locations_ar.txt'
SLANG_DICT_FILE = 'data/slang_dict.csv'
CATEGORIES_DICT_FILE = 'data/categories_dict.txt'

# ---------------------------------
# Twitter/Google/Bing 
# ---------------------------------

TWITTER_KEY = {'consumer_key': cfg['online_keys']['twitter']['consumer_key'], 'consumer_secret': cfg['online_keys']['twitter']['consumer_secret'], 'access_token': cfg['online_keys']['twitter']['access_token'], 'access_token_secret': cfg['online_keys']['twitter']['access_secret']}
GOOGLE_KEY = cfg['online_keys']['google']
BING_KEY = cfg['online_keys']['bing']

LOG_FILE_LOCATION = cfg['logfile']

PERSISTER_FOLDER = cfg['persister_folder']
# ---------------------------------
# Log File
# ---------------------------------

# Initialize the logger
logging.basicConfig(filename=LOG_FILE_LOCATION,format='%(levelname)s: %(module)s: %(funcName)s: %(message)s', level=logging.INFO)
logger = logging.getLogger('__name__')

# ---------------------------------
# Helpful Functions  
# ---------------------------------		

def to_datetime(tweet):
	return datetime.strptime(tweet.get('created_at',None),'%a %b %d %H:%M:%S +0000 %Y')


def collect_tweets():
	"""
	Collect tweets matching input keywords in KEYWORD_DICT_FILE
	:return: writes into Redis Channel: REDIS_NAMESPACE:REDIS_NAME_RAW_TWEETS
	"""
	write_channel = '%s:%s' % (REDIS_NAMESPACE, REDIS_NAME_RAW_TWEETS)
	write_channel_arabic_tweets = '%s:%s' % (REDIS_NAMESPACE, REDIS_NAME_RAW_ARABIC_TWEETS)
	twitter_collector = TwitterCollector(r_db=REDIS_DB, r_channel=write_channel, r_arabic_channel=write_channel_arabic_tweets,
										keyword_dict_file=KEYWORD_DICT_FILE, twitter_key=TWITTER_KEY)
	logger.info("Starting Collector. Will read from twitter and write into %s", write_channel)
	twitter_collector.get_tweets()


def classify_tweets_paco():
	""" Uses Paco's classifier
	Reads from redis channel REDIS_NAMESPACE:REDIS_NAME_RAW_TWEETS, checks if the tweet is about traffic
	then write to the redis channel: REDIS_NAMESPACE:REDIS_NAME_TRAFFIC_TWEETS
	:return:
	"""
	read_channel = '%s:%s' % (REDIS_NAMESPACE, REDIS_NAME_RAW_TWEETS)
	write_channel = '%s:%s' % (REDIS_NAMESPACE, REDIS_NAME_TRAFFIC_TWEETS)
	non_traffic_tweets_channel = '%s:%s' % (REDIS_NAMESPACE, REDIS_NAME_NON_TRAFFIC_TWEETS)

	# tweet_classifier = TwitterClassifier(method='Keyword', keyword_dictionary_file=KEYWORD_DICT_FILE)
	logger.info("Starting Classifier. Will read from %s and write into %s", read_channel, write_channel)

	# Integrating Paco's classifier
	tweets = []
	tweets_file_name = 'traffic_classifier/data/tweets_200.out'
	while True:
		# read from Redis channel: REDIS_NAMESPACE:REDIS_NAME_RAW_TWEETS
		data = REDIS_DB.blpop(read_channel)
		if len(data) != 2:
			continue
		data = data[1]
		logger.debug("READ from redis [type:%s]: %s", type(data), data)
		tweets.append(data.replace('\r\n', ' ').replace('\n', ' '))
		if len(tweets) == 200:
			logger.info("Running classifier on 200 Tweets")
			# 1. Create tweets file
			with open(tweets_file_name, 'w') as outfile:
				outfile.write('\n'.join(tweets))
			# 2. Run classifier
			subprocess.call(['./traffic_classifier/classifydata.sh', tweets_file_name])
			# 3. Read the output file, and write tweets into corresponding redis channels.
			with open(tweets_file_name+'.classification.results') as outfile:
				for idx, line in enumerate(outfile):
					decision = line.strip()
					data = json.loads(tweets[idx])
					if decision == 'Y':
						data['is_about_traffic'] = True
						REDIS_DB.rpush(write_channel, json.dumps(data))
					elif decision == 'N':
						data['is_about_traffic'] = False
						REDIS_DB.rpush(non_traffic_tweets_channel, json.dumps(data))
			# 4. Empty tweets list
			tweets = []

def classify_arabic_tweets():
	read_channel = '%s:%s' % (REDIS_NAMESPACE, REDIS_NAME_RAW_ARABIC_TWEETS)
	write_channel = '%s:%s' % (REDIS_NAMESPACE, REDIS_NAME_TRAFFIC_ARABIC_TWEETS)
	non_relevant_arabic_tweets_channel = '%s:%s' % (REDIS_NAMESPACE, REDIS_NAME_NON_TRAFFIC_ARABIC_TWEETS)
	arabic_tweet_classifier = ArabicTwitterClassifier(method='Keyword', keyword_dictionary_file=KEYWORD_DICT_FILE)
	logger.info("Starting Arabic Classifier. Will read from %s and write into %s", read_channel, write_channel)
	while True:
		data = REDIS_DB.blpop(read_channel)
		if len(data) != 2:
			continue
		data = data[1]
		logger.debug("READ from redis [type:%s]: %s", type(data), data)
		data = json.loads(data)
		if arabic_tweet_classifier.is_about_traffic(data):
			data['is_about_traffic'] = True
			REDIS_DB.rpush(write_channel, json.dumps(data))
		else:
			data['is_about_traffic'] = False
			REDIS_DB.rpush(non_relevant_arabic_tweets_channel, json.dumps(data))


def extract_entities():
	"""
	Extract location from tweets. Blocking reads from read_channel,
	extract locations, then writes into write channel
	!! This also checks for the presence of bad words in the tweet text
	:return: writes into write channel
	"""
	read_channel = '%s:%s' % (REDIS_NAMESPACE, REDIS_NAME_TRAFFIC_TWEETS)
	write_channel = '%s:%s' % (REDIS_NAMESPACE, REDIS_NAME_LOCATED_TRAFFIC_TWEETS)
	non_located_traffic_tweets_channel = '%s:%s' % (REDIS_NAMESPACE, REDIS_NAME_NON_LOCATED_TRAFFIC_TWEETS)
	worldwide_tweets_channel = '%s:%s' % (REDIS_NAMESPACE, REDIS_NAME_WORLDWIDE_GEOLOCATED_TWEETS)

	twitter_location_er = TwitterLocationER(location_dictionary_file=GEOCODED_LOCATION_DICT_FILE)
	location_geocoding = LocationGeocoding('en', google_key=GOOGLE_KEY, bing_key=BING_KEY, country_code='QA', geocoded_location_file=GEOCODED_LOCATION_DICT_FILE)
	slang_detection = SlangDetection(slang_dictionary_file=SLANG_DICT_FILE)
	incident_classifier = IncidentClassifier(categories_dictionary_file=CATEGORIES_DICT_FILE)
	logger.info("Starting LocationTagger. Will read from %s and write into %s", read_channel, write_channel)

	while True:
		# read from Redis channel: REDIS_NAMESPACE:REDIS_NAME_RAW_TWEETS
		data = REDIS_DB.blpop(read_channel)
		if len(data) != 2:
			continue
		data = data[1]
		data = json.loads(data)

		is_worldwide_tweet = location_geocoding.is_tweet_outside_qatar(data)
		if is_worldwide_tweet:
			category = incident_classifier.get_tweet_category(data['text'], 'en')
			data['category'] = category
			REDIS_DB.rpush(worldwide_tweets_channel, json.dumps(data))
			logger.info("Tweet outside Qatar")
		else:
			locations = twitter_location_er.find_locations(data)
			bad_words = slang_detection.contains_bad_words(data['text'])
			has_blacklisted_location = has_black_listed_location(data['text'])

			if len(locations) > 0 and has_blacklisted_location == False:
				geocoded_locations = [location_geocoding.geocode_location(location) for location in locations]
				category = incident_classifier.get_tweet_category(data['text'], 'en')
				data['contains_traffic_locations'] = True
				data['traffic_locations'] = geocoded_locations
				data['bad_words'] = list(bad_words)
				data['contains_bad_words'] = True if len(bad_words) > 0 else False
				data['category'] = category
				# Write to a new Redis channel: REDIS_NAMESPACE:REDIS_NAME_TRAFFIC_TWEETS
				REDIS_DB.rpush(write_channel, json.dumps(data))
				logger.info("New located tweets:%s\n Locations: %s", data['text'], list(locations))
			else:
				# add the tweet to the end, and make sure the list has at most 1M tweets
				data['contains_traffic_locations'] = False
				REDIS_DB.rpush(non_located_traffic_tweets_channel, json.dumps(data))
				REDIS_DB.ltrim(non_located_traffic_tweets_channel, -1000000, -1)

def extract_ar_entities():
	read_channel = '%s:%s' % (REDIS_NAMESPACE, REDIS_NAME_TRAFFIC_ARABIC_TWEETS)
	write_channel = '%s:%s' % (REDIS_NAMESPACE, REDIS_NAME_LOCATED_ARABIC_TRAFFIC_TWEETS)
	non_located_arabic_traffic_tweets_channel = '%s:%s' % (REDIS_NAMESPACE, REDIS_NAME_NON_LOCATED_ARABIC_TRAFFIC_TWEETS)

	arabic_twitter_location_er = ArabicTwitterLocationER(location_dictionary_ar_file=GEOCODED_LOCATION_AR_DICT_FILE)
	location_geocoding = LocationGeocoding('ar', google_key=GOOGLE_KEY, bing_key=BING_KEY, country_code='QA',geocoded_location_file=GEOCODED_LOCATION_AR_DICT_FILE)
	incident_classifier = IncidentClassifier(categories_dictionary_file=CATEGORIES_DICT_FILE)

	while True:
		data = REDIS_DB.blpop(read_channel)
		if len(data) != 2:
			continue
		data = data[1]
		data = json.loads(data)
		locations = arabic_twitter_location_er.find_locations(data['text'])
		has_blacklisted_location = has_ar_blacklisted_location(data['text'])
		#is_qatar_doha_expression_exist = arabic_twitter_location_er.is_tweet_has_local_expressions(data['text'].lower())
		if len(locations) > 0 and has_blacklisted_location == False:
			geocoded_locations = [location_geocoding.geocode_location(location) for location in locations]
			category = incident_classifier.get_tweet_category(data['text'], 'ar')
			data['contains_traffic_locations'] = True
			data['traffic_locations'] = geocoded_locations
			data['category'] = category
			REDIS_DB.rpush(write_channel, json.dumps(data))
		else:
			data['contains_traffic_locations'] = False
			REDIS_DB.rpush(non_located_arabic_traffic_tweets_channel, json.dumps(data))
			REDIS_DB.ltrim(non_located_arabic_traffic_tweets_channel, -1000000, -1)


def persist_tweets(redis_channel, folder_name):
	"""
	Persist tweets in a given redis_channel into a folder_name
	:param redis_channel: the redis list from which we should read tweets
	:param folder_name: the name of the folder in which tweets should be created.
	:return: Nothing.
	"""

	folder = PERSISTER_FOLDER + '/' + folder_name
	# check if directory exists, and create it if not.
	if not os.path.exists(folder):
		os.makedirs(folder)

	twitter_persister = TwitterPersister(persister_folder=folder, file_size=100000)
	redis_tweets_channel = '%s:%s' % (REDIS_NAMESPACE, redis_channel)
	while True:
		data = REDIS_DB.blpop(redis_tweets_channel)
		if len(data) != 2:
			continue
		data = data[1]
		twitter_persister.append_tweet(data.replace('\r\n', ' ').replace('\n', ' '))


def persist_tweets_mongodb(redis_channel, collection):
	"""
	Persist tweets in a given redis_channel into  collection on mongodb
	"""

	redis_tweets_channel = '%s:%s' % (REDIS_NAMESPACE, redis_channel)
	while True:
		data = REDIS_DB.blpop(redis_tweets_channel)
		if len(data) != 2:
			continue
		data = data[1]
		json_data = json.loads(data.replace('\r\n', ' ').replace('\n', ' '))
		# Convert datetime
		json_data['created_at'] = to_datetime(json_data)
		collection.insert(json_data)



if __name__ == '__main__':

	collector = multiprocessing.Process(name='Collector', target=collect_tweets)
	collector.start()

	classifier = multiprocessing.Process(name='Classifier', target=classify_tweets_paco)
	classifier.start()

	ar_classifier = multiprocessing.Process(name='ClassifierAR', target=classify_arabic_tweets)
	ar_classifier.start()

	location_tagger = multiprocessing.Process(name='LocationER', target=extract_entities)
	location_tagger.start()

	location_tagger_ar = multiprocessing.Process(name='ARLocationER', target=extract_ar_entities)
	location_tagger_ar.start()

	# Store data, we might need them in the future
	persist_non_traffic_tweets = multiprocessing.Process(name='PERSIST_COLLECTION_ENG_NON_TRAFFIC', target=persist_tweets_mongodb, args=(REDIS_NAME_NON_TRAFFIC_TWEETS, COLLECTION_ENG_NON_TRAFFIC ))
	persist_non_traffic_tweets.start()

	persist_non_traffic_arabic_tweets = multiprocessing.Process(name='PERSIST_COLLECTION_AR_NON_TRAFFIC', target=persist_tweets_mongodb, args=(REDIS_NAME_NON_TRAFFIC_ARABIC_TWEETS, COLLECTION_AR_NON_TRAFFIC))
	persist_non_traffic_arabic_tweets.start()

	persist_non_located_traffic_tweets = multiprocessing.Process(name='PERSIST_COLLECTION_ENG_NON_LOCATED_TRAFFIC', target=persist_tweets_mongodb, args=(REDIS_NAME_NON_LOCATED_TRAFFIC_TWEETS, COLLECTION_ENG_NON_LOCATED_TRAFFIC))
	persist_non_located_traffic_tweets.start()

	persist_non_located_arabic_traffic_tweets = multiprocessing.Process(name='PERSIST_COLLECTION_AR_NON_LOCATED_TRAFFIC', target=persist_tweets_mongodb, args=(REDIS_NAME_NON_LOCATED_ARABIC_TRAFFIC_TWEETS, COLLECTION_AR_NON_LOCATED_TRAFFIC))
	persist_non_located_arabic_traffic_tweets.start()

	# add located_traffic_tweets
	persist_eng_located_traffic_tweets_mongodb = multiprocessing.Process(name='PERSIST_COLLECTION_ENG_LOCATED_TRAFFIC_QA', target=persist_tweets_mongodb, args=( REDIS_NAME_LOCATED_TRAFFIC_TWEETS ,COLLECTION_ENG_LOCATED_TRAFFIC_QA ))
	persist_eng_located_traffic_tweets_mongodb.start()

	persist_ar_located_traffic_tweets_qa_mongodb = multiprocessing.Process(name='PERSIST_COLLECTION_AR_LOCATED_TRAFFIC_QA', target=persist_tweets_mongodb, args=( REDIS_NAME_LOCATED_ARABIC_TRAFFIC_TWEETS ,COLLECTION_AR_LOCATED_TRAFFIC_QA ))
	persist_ar_located_traffic_tweets_qa_mongodb.start()

	persist_eng_located_traffic_tweets_ww_mongodb = multiprocessing.Process(name='PERSIST_COLLECTION_ENG_LOCATED_TRAFFIC_WORLDWIDE', target=persist_tweets_mongodb, args=( REDIS_NAME_WORLDWIDE_GEOLOCATED_TWEETS ,COLLECTION_ENG_LOCATED_TRAFFIC_WORLDWIDE ))
	persist_eng_located_traffic_tweets_ww_mongodb.start()
