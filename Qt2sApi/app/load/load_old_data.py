import os
from flask import Flask
from flask import render_template
from pymongo import MongoClient, errors
from datetime import datetime
from config import *
import json
import string
import re
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.tokenize import RegexpTokenizer
from collections import defaultdict


CATEGORIES_DICT_FILE = 'data/categories_dict.txt'


try:
	connection = MongoClient(MONGODB_HOST, MONGODB_PORT, connect=False)
	print "<DEBUG>: Connected to MongoDB successfully!!!"


	COLLECTION_AR_NON_TRAFFIC = connection[DBS_NAME][COLLECTION_AR_NON_TRAFFIC_NAME]
	COLLECTION_ENG_NON_TRAFFIC = connection[DBS_NAME][COLLECTION_ENG_NON_TRAFFIC_NAME]

	COLLECTION_AR_NON_LOCATED_TRAFFIC = connection[DBS_NAME][COLLECTION_AR_NON_LOCATED_TRAFFIC_NAME]
	COLLECTION_ENG_NON_LOCATED_TRAFFIC = connection[DBS_NAME][COLLECTION_ENG_NON_LOCATED_TRAFFIC_NAME]

	COLLECTION_ENG_LOCATED_TRAFFIC = connection[DBS_NAME][COLLECTION_ENG_LOCATED_TRAFFIC_NAME]
	COLLECTION_AR_LOCATED_TRAFFIC = connection[DBS_NAME][COLLECTION_AR_LOCATED_TRAFFIC_NAME]

except errors.ConnectionFailure, e:
   print "Could not connect to MongoDB: %s" % e

# ---------------------------------
# Helpful Functions  
# ---------------------------------		

def getWords(text):
	return re.compile('\w+').findall(text)

def clean_text(text):
	text = re.sub(r"http\S+", "", text)
	text = ' '.join([w for s in sent_tokenize(text) for w in word_tokenize(s) if w not in string.punctuation])
	return text


def ngrams(inputText, n):
	inputText = getWords(inputText)
	output = []
	for i in range(len(inputText)-n+1):
		g = ' '.join(inputText[i:i+n])
		output.append(g)
	return output


def to_datetime(tweet):
	return datetime.strptime(tweet.get('created_at',None),'%a %b %d %H:%M:%S +0000 %Y')

# ---------------------------------
# Classes
# ---------------------------------		

class IncidentClassifier:
	def __init__(self, categories_dictionary_file=None):
		if categories_dictionary_file is None:
			raise Exception("Error: You should provide a path to the categories dictionary file")
		word_cat_label = {}
		with open(categories_dictionary_file) as f:
			for line in f:
				categories = json.loads(line)
				for cat_label, cat_definition in categories.iteritems():
					for word in cat_definition:
						word_cat_label[clean_text(word.lower())] = cat_label
		self.categories = word_cat_label

	def get_tweet_category(self, text):
		found_categories = defaultdict(int)
		text = clean_text(text.lower())
		for cat_word in self.categories:
			category_len = len(cat_word.split(' '))
			ngrams_list = ngrams(text, category_len)
			for ngram in ngrams_list:
				if cat_word == ngram:
					found_categories[self.categories[cat_word]] += 1
		if len(found_categories) != 0:
			return sorted(found_categories, key=found_categories.get, reverse=True)[0]
		else:
			return 'Others'


incident_classifier = IncidentClassifier(categories_dictionary_file=CATEGORIES_DICT_FILE)


# ---------------------------------
# Loading tweets  
# ---------------------------------		
with open('old_located_traffic_tweets', 'r') as f:
	for line in f:
		json_data = json.loads(line.replace('\r\n', ' ').replace('\n', ' '))
		json_data['created_at'] = to_datetime(json_data)
		json_data['category'] = incident_classifier.get_tweet_category(json_data["text"])
		if json_data["is_from_qatar"] == True:
			COLLECTION_ENG_LOCATED_TRAFFIC.insert(json_data)

print "<DEBUG>: Finished"

