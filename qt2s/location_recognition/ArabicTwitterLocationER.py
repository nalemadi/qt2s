#!/usr/bin/python
# -*- coding: UTF-8 -*-

__author__ = 'noora'

import logging

from resources.resources import clean_ar_text
import json

logger = logging.getLogger('__name__')

class ArabicTwitterLocationER:
	def __init__(self, location_dictionary_ar_file=None):
		if location_dictionary_ar_file is None:
			logger.error("You should provide a path to the Arabic location dictionary file")
			raise Exception("Error: You should provide a path to the Arabic location dictionary file")
		locations = []
		with open(location_dictionary_ar_file) as f:
			for line in f:
				if len(line.strip()) == 0:
					continue
				location = json.loads(line)
				locations.append(location['name'].lower())
		self.locations = [clean_ar_text(location) for location in locations]
		logger.info('New Instance\n Arabic Locations considered: %s', self.locations)

	def find_locations(self, text):
		"""
		Checks if a location exist in the text.
		If the location name is one word, verify if it's among the tokens of the input text.
		ElseIF the location name is multiword, perform a simple substring matching.
		:param text: body of the tweet
		:return: set of locations found in the text.
		"""
		found_locations = set()
		text = clean_ar_text(text.lower())
		#twords = text.split()
		for location in self.locations:
			if location in text and u'دوار اللؤلؤة' not in text:
				found_locations.add(location)
			"""
			if len(location.split()) > 1 and location in text:
				found_locations.add(location)
			elif len(location.split()) ==1 and location in twords:
				found_locations.add(location)
			"""
		logger.debug('Arabic Locations found: %s', found_locations)
		return found_locations

	def is_tweet_has_local_expressions(self, data_text):
		"""
		not used
		:param data_text:
		:return:
		"""
		has_local_expressions = False
		for expression in self.locations:
			if expression in data_text:
				has_local_expressions = True
		return has_local_expressions
