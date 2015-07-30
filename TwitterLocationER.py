__author__ = 'sofiane'

import logging
import re
import string
import logging
from nltk.tokenize import word_tokenize, sent_tokenize

logger = logging.getLogger('__name__')


class TwitterLocationER:
	def __init__(self, location_dictionary_file=None, slang_dictionary_file=None):
		if location_dictionary_file is None:
			logger.error("You should provide a path to the location dictionary file")
			raise Exception("Error: You should provide a path to the location dictionary file")
		if slang_dictionary_file is None:
			logger.warning("No slang dictionary provided. The program will not check for bad words")
		locations = [location.split(';')[2].lower() \
					 for location in open(location_dictionary_file).read().split('\n')[:-1]]
		self.locations = [self.clean_text(location) for location in locations]
		self.bad_words = [w.strip().lower() for w in
						  open(slang_dictionary_file).read().split('\n')[:-1]]

		logger.debug('New Instance\n locations: %s', self.locations)

	@staticmethod
	def clean_text(text):
		"""
		Cleans a text by removing punctuations, urls, and non ascii characters.
		:param text: input text
		:return: clean text
		"""
		#TODO: to careful on the cleaning. Remove urls, #, @, and other punctuation characters.
		# 1. remove urls
		text = re.sub(r"http\S+", "", text)

		# 2. tokenize and remove punctuations: !"#$%&'()*+,-./:;<=>?@[\]^_`{|}~
		text = ' '.join([w for s in sent_tokenize(text) for w in word_tokenize(s) if w not in string.punctuation])

		# TODO: make sure we want to keep this one - 3. remove non ascii characters
		#text = ''.join([c for c in text if c in string.printable])
		return text

	def contains_bad_words(self, text):
		"""
		Check the presence of slang language in a string
		:param text: body of the tweet
		:return: list of bad words found in the input text
		"""
		text = [w for s in sent_tokenize(text) for w in word_tokenize(s) if w not in string.punctuation]
		found_bad_words = [w for w in text if w in self.bad_words]
		return set(found_bad_words)

	def find_locations_naive(self, text):
		"""
		Applies a simple substring matching between locations and the text of a tweet.
		:param text: Content of a tweet
		:return: a list of locations found in the tweet.
		"""
		text = self.clean_text(text.lower())
		logger.debug('cleaned text: %s', text)
		found_locations = set()
		for location in self.locations:
			if location in text:
				found_locations.add(location)
		logger.debug('Locations found: %s', found_locations)
		return found_locations

	def find_locations(self, text):
		"""
		Checks if a location exist in the text.
		If the location name is one word, verify if it's among the tokens of the input text.
		ElseIF the location name is multiword, perform a simple substring matching.
		:param text: body of the tweet
		:return: set of locations found in the text.
		"""
		found_locations = set()
		text = self.clean_text(text.lower())
		twords = text.split()
		for location in self.locations:
			if len(location.split()) > 1 and location in text:
				found_locations.add(location)
			elif len(location.split()) ==1 and location in twords:
				found_locations.add(location)
		logger.debug('Locations found: %s', found_locations)
		return found_locations








