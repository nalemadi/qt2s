__author__ = 'sofiane'


import logging

from resources.resources import clean_text
from resources.resources import ngrams
import json

logger = logging.getLogger('__name__')


class TwitterLocationER:
	def __init__(self, location_dictionary_file=None):
		if location_dictionary_file is None:
			logger.error("You should provide a path to the location dictionary file")
			raise Exception("Error: You should provide a path to the location dictionary file")
		locations = {}
		with open(location_dictionary_file) as f:
			for line in f:
				if len(line.strip()) == 0:
					continue
				location = json.loads(line)
				#locations.append(location['name'].lower())
				locations[clean_text(location['name'].lower())] = location['name'].lower()
				alternatives = location['alternatives']
				if alternatives is not None:
					for alternative in alternatives:
						locations[clean_text(alternative.lower())] = location['name'].lower()
		#self.locations = [clean_text(location) for location in locations]
		self.locations = locations
		logger.info('New Instance\n Locations considered: %s', self.locations)

	def find_locations_naive(self, text):
		"""
		Applies a simple substring matching between locations and the text of a tweet.
		:param text: Content of a tweet
		:return: a list of locations found in the tweet.
		"""
		text = clean_text(text.lower())
		logger.debug('cleaned text: %s', text)
		found_locations = set()
		for location in self.locations:
			if location in text:
				found_locations.add(location)
		logger.debug('Locations found: %s', found_locations)
		return found_locations

	def find_locations_substring(self, text):
		"""
		Checks if a location exist in the text.
		If the location name is one word, verify if it's among the tokens of the input text.
		ElseIF the location name is multiword, perform a simple substring matching.
		:param text: body of the tweet
		:return: set of locations found in the text.
		"""
		found_locations = set()
		text = clean_text(text.lower())
		twords = text.split()
		for location in self.locations:
			if len(location.split()) > 1 and location in text:
				found_locations.add(location)
			elif len(location.split()) ==1 and location in twords:
				found_locations.add(location)
		logger.debug('Locations found: %s', found_locations)
		return found_locations

	def find_locations(self, text):
		"""
		Checks if a location exist in the text.
		using ngrams algorithm to deal with mutiword location
		:param text: body of the tweet
		:return: set of locations found in the text.
		"""
		found_locations = set()
		text = clean_text(text.lower())
		for location_key in self.locations.keys():
			location_len = len(location_key.split(' '))
			ngrams_list = ngrams(text, location_len)
			for ngram in ngrams_list:
				if location_key == ngram:
					found_locations.add(self.locations[location_key])
		return found_locations

#if __name__ == '__main__':
#	twitterLocationER = TwitterLocationER(location_dictionary_file='../data/geolocated_locations.txt')
#	print twitterLocationER.find_locations('traffic jam in cornishe and majlis al tawon st or al sadd st')