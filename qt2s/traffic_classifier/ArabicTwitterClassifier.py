__author__ = 'noora'

import logging
from resources.resources import clean_ar_text
logger = logging.getLogger(__name__)


class ArabicTwitterClassifier:

	def __init__(self, method=None, keyword_dictionary_file=None, model=None):
		if method == 'keyword' and not keyword_dictionary_file:
			logger.error('Error: you should provide a path to the keywords file')
			raise Exception('Error: you should provide a path to the keywords file')
		self.keywords = [clean_ar_text(w.decode('utf-8').strip().lower()) for w in open(keyword_dictionary_file).read().split('\n')]

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
		text = clean_ar_text(text.lower())

		for keyword in self.keywords:
			if keyword in text:
				logger.debug("This tweet [%s] is about traffic: %s", text, keyword)
				return True
		logger.debug("This tweet [%s] is NOT about traffic", text)
		return False

	#def is_about_traffic(self, tweet):
	#	return True
