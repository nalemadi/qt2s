__author__ = 'sofiane'

import logging
from resources.resources import clean_text
logger = logging.getLogger(__name__)


class TwitterClassifier:
	def __init__(self, method=None, keyword_dictionary_file=None, model=None):
		if method == 'keyword' and not keyword_dictionary_file:
			logger.error('Error: you should provide a path to the keywords file')
			raise Exception('Error: you should provide a path to the keywords file')
		self.keywords = [clean_text(w.strip().lower()) for w in open(keyword_dictionary_file).read().split(',')]

		if method == 'classifier' and not model:
			logger.error('Error: you should provide a path to the classifier model')
			raise Exception('Error: you should provide a path to the classifier model')

	def is_about_traffic(self, tweet):
		"""
		Check whether a tweet is about traffic or not.
		This implementation relies on the existence of some keywords in the tweet.
		:param tweet: a json object of the tweet
		:return: True if the tweet text has a location name, False otherwise.
		"""
		text = tweet['text']
		text = clean_text(text.lower())

		for keyword in self.keywords:
			if keyword in text:
				logger.debug("This tweet [%s] is about traffic: %s", text, keyword)
				return True
		logger.debug("This tweet [%s] is NOT about traffic", text)
		return False

	def _generate_tweets_file(self):
		"""
		Reads from redis channel of tweets 500 tweets and write them into a file
		:return: file called tweets_500.out that will be used by Paco's classifier
		"""






