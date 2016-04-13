import sys
sys.path.append('../')

from resources.mongodb_config import *
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

from resources.mongodb_config import *

CATEGORIES_DICT_FILE = 'data/categories_dict.txt'

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

# ---------------------------------
# Helpful Functions
# ---------------------------------

def to_datetime(tweet):
	return datetime.strptime(tweet.get('created_at',None),'%a %b %d %H:%M:%S +0000 %Y')

def classify_data(FILE_DIR):
	twitter_location_er = TwitterLocationER(location_dictionary_file=GEOCODED_LOCATION_DICT_FILE)
	location_geocoding = LocationGeocoding('en', google_key=GOOGLE_KEY, bing_key=BING_KEY, country_code='QA', geocoded_location_file=GEOCODED_LOCATION_DICT_FILE)
	slang_detection = SlangDetection(slang_dictionary_file=SLANG_DICT_FILE)
	incident_classifier = IncidentClassifier(categories_dictionary_file=CATEGORIES_DICT_FILE)

	while True:
		with open(FILE_DIR, 'r') as f:
			for line in f:
				data = json.loads(line.replace('\r\n', ' ').replace('\n', ' '))
				data['created_at'] = to_datetime(data)
				is_worldwide_tweet = location_geocoding.is_tweet_outside_qatar(data)

				if is_worldwide_tweet:
					category = incident_classifier.get_tweet_category(data['text'])
					data['category'] = category

					COLLECTION_ENG_LOCATED_TRAFFIC_WORLDWIDE.insert(data)

				else:
					locations = twitter_location_er.find_locations(data['text'])
					bad_words = slang_detection.contains_bad_words(data['text'])
					is_from_qatar = location_geocoding.is_tweet_from_qatar(data)
					if len(locations) > 0 and 'pearl jam' not in data['text'].lower():
						geocoded_locations = [location_geocoding.geocode_location(location) for location in locations]
						category = incident_classifier.get_tweet_category(data['text'])
						data['is_from_qatar'] = is_from_qatar
						data['contains_traffic_locations'] = True
						data['traffic_locations'] = geocoded_locations
						data['bad_words'] = list(bad_words)
						data['contains_bad_words'] = True if len(bad_words) > 0 else False
						data['category'] = category
						COLLECTION_ENG_LOCATED_TRAFFIC_QA.insert(data)


# ---------------------------------
# Loading tweets  
# ---------------------------------
if __name__ == '__main__':
	classify_data('old_located_traffic_tweets.txt')
	classify_data('new_located_traffic_tweets.txt')

