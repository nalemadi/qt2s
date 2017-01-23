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

	def find_locations(self, tweet):
		"""
		Checks if a location exist in the text.
		using ngrams algorithm to deal with multiword location
		:param text: body of the tweet
		:return: set of locations found in the text.
		"""
		expressions = ['qatar', 'doha']
		found_locations = set()
		text = tweet['text']
		text = clean_text(text.lower())
		for location_key in self.locations.keys():
			location_len = len(location_key.split(' '))
			ngrams_list = ngrams(text, location_len)
			for ngram in ngrams_list:
				if location_key == ngram:
					if ngram == "the mall" or ngram == "the pearl" or ngram == "pearl" or ngram == "landmark":
						if any(x in text for x in expressions) == False or self.is_tweet_from_qatar(tweet) == False:
							print 'not related'
							continue
						else:
							found_locations.add(self.locations[location_key])
					found_locations.add(self.locations[location_key])
		return found_locations

	def is_tweet_from_qatar(self, tweet):
		""" Checks whether a tweet is from Qatar or not. A tweet is considered from Qatar if
		and only if: it has geo-coordinates inside Qatar, or the user has the name of
		a Qatari location in the location attribute of his profile.
		Created by Noora, Edited by Sofiane
		:param tweet: Tweet as a Json object.
		:return: Boolean
		"""
		if 'coordinates' not in tweet.keys() and 'user' not in tweet.keys():
			return False

		if tweet['coordinates'] is not None:
			lng = tweet['coordinates']['coordinates'][0]
			lat = tweet['coordinates']['coordinates'][1]
			# Qatar boundingBox 50.7048,24.4708,51.7371,26.2057
			lat_max = 26.2057
			lat_min = 24.4708
			lng_max = 51.7371
			lng_min = 50.7048
			if lat_min <= lat <= lat_max and lng_min <= lng <= lng_max:
				return True
			else:
				return False
		if tweet['user']['location'] is None:
			return False
		else:
			#qatar_locations = self.get_qatar_locations(lang)
			user_location = clean_text(tweet['user']['location'].lower())
			user_locations = user_location.split()
			for usr_location in user_locations:
				if usr_location in self.locations:
					return True
			return False
"""
if __name__ == '__main__':
	twitterLocationER = TwitterLocationER(location_dictionary_file='../data/geolocated_locations.txt')
	#print twitterLocationER.find_locations('traffic jam in the mall and corniche')
"""