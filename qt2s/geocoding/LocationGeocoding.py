#!/usr/bin/python
# -*- coding: UTF-8 -*-

__author__ = 'sofiane'
import urllib
import urllib2
import json
import logging
import googlemaps
from googlemaps.exceptions import ApiError, TransportError, Timeout, HTTPError
from resources.resources import clean_text

logger = logging.getLogger('__name__')


class LocationGeocoding:
	QATAR_DOHA_TEXT_EN = ' Doha Qatar'
	QATAR_TEXT_EN = 'Qatar'
	QATAR_DOHA_TEXT_AR = u' الدوحة قطر'

	def __init__(self, language, google_key=None, bing_key=None, country_code='QA', geocoded_location_file=None):
		self.language = language
		self.geocoded_location_files = geocoded_location_file
		self.google_key = google_key
		self.bing_key = bing_key
		self.country_code = country_code
		if language == 'en':
			self.qatar_doha_query = self.QATAR_DOHA_TEXT_EN
		elif language == 'ar':
			self.qatar_doha_query = self.QATAR_DOHA_TEXT_AR

		self.geocoded_locations = dict()
		if geocoded_location_file is None:
			print 'None file'
		else:
			with open(geocoded_location_file) as f:
				for line in f:
					if len(line.strip()) == 0:
						continue
					location = json.loads(line)
					self.geocoded_locations[location['name'].lower()] = location

	def google_geocoding(self, location):
		"""
		Using GoogleMaps api to geocode a location.
		:param location: text describing a location name
		:return: a location object with: formatted_address, lat, lng attributes
		"""
		# TODO: Try to consider all location from the country_code.
		try:
			gmaps = googlemaps.Client(key=self.google_key)
			# Use components to make sure the first result is about Qatar.
			res = gmaps.geocode(location, components={'country': self.country_code})
			if not res or len(res) == 0:
				return None
			# Thanks to components, we can consider the first result only.
			g_location = self._format_google_location(res[0])
			return g_location
		except ApiError as e:
			logger.error("problem with googlemap geocoding (ApiError): %s", e)
			return None
		except HTTPError as e:
			logger.error("problem with googlemap geocoding (HTTPError): %s", e)
			return None
		except Timeout as e:
			logger.error("problem with googlemap geocoding (Timeout): %s", e)
			return None
		except TransportError as e:
			logger.error("problem with googlemap geocoding (TransportError): %s", e)
			return None

	def bing_geocoding(self, location):
		"""
		Using Bing Map api to geocode a location
		:param location:
		:return:
		"""
		basepath = 'http://dev.virtualearth.net/REST/v1/Locations?'
		location += self.qatar_doha_query.encode('utf-8')
		formattedQuery = urllib.quote(location)
		requestURL = '{}q={}&key={}'.format(basepath, formattedQuery, self.bing_key)
		#print requestURL
		obj = self.run_request(requestURL)

		if 'resourceSets' not in obj.keys():
			return None

		estimatedTotal = obj['resourceSets'][0]['estimatedTotal']
		if estimatedTotal == 0:
			return None
		results = obj['resourceSets'][0]['resources']
		if len(results) == 0:
			return None
		indx = -1
		for i, result in enumerate(results):
			address = result['address']
			if 'countryRegion' not in address.keys():
				return None
			if address['countryRegion'] == 'Qatar':
				indx = i
				break
		if indx == -1:
			return None
		return  self._format_bing_location(results[indx])

	def nominatim_geocoding(self, location):
		"""
		Using nominatim to geocode a location
		:param location:
		:return:
		"""
		location += ' '+'Qatar'
		basepath = "[REDACTED_URL]     "
		params = {"addressdetails":1,"format":"json", "country":"QA", "q":location}
		try:
			response = urllib2.urlopen(basepath+urllib.urlencode(params))
			results = response.read()

		except:
			logger.error('Unable to reach Nominatim Server. Request for location: {}'.format(location))
			return None

		try:
			results = json.loads(results)
			#print results
			indx = -1
			for i, result in enumerate(results):
				if result['address']['country_code'] == 'qa':
					indx = i
					break
			if indx == -1:
				return None
			return  self._format_nominatim_format(results[indx])
			#print '%s\t%s' % (location.strip(), results[0]['address']['country_code'])
		except:
			print '%s\t%s' % (location.strip(), 'None')

	def google_geocoding_from_scratch(self, location):
		basepath = 'https://maps.googleapis.com/maps/api/geocode/json?'
		params = urllib.urlencode({'address': location, 'components': {'country :'+self.country_code},
								   'key': self.google_key})
		#print basepath+params
		obj = self.run_request(basepath + params)
		if 'results' not in obj.keys() or len(obj['results']) == 0:
			return None

		results = obj['results']
		# check if there's a result about our country code: Qatar
		indx = -1
		for i, result in enumerate(results):
			country = result['address_components'][-1]
			if country['short_name'] == self.country_code:
				indx = i
				break
		if indx == -1:
			return None
		return self._format_google_location(results[indx])

	def _format_google_location(self, g_location):
		"""
		Extracts relevant information from googlemaps results.
		:param g_location: one googlemaps result
		:return: dictionary of a location with: formatted_address, lat, lng
		"""
		if 'formatted_address' not in g_location.keys():
			return None
		if 'geometry' not in g_location.keys() or 'location' not in g_location['geometry'].keys()\
				or 'lat' not in g_location['geometry']['location'].keys():
			return None

		location = dict()
		location['formatted_address'] = g_location['formatted_address']
		location['lat'] = g_location['geometry']['location']['lat']
		location['lng'] = g_location['geometry']['location']['lng']
		return location

	def _format_bing_location(self, b_location):
		"""
		Extracts relevant information from bingmap result
		:param b_location:
		:return: dictionary of a location with: formatted_address, lat, lng
		"""
		if 'address' not in b_location.keys() or 'formattedAddress' not in b_location['address'].keys():
			return None
		if 'point' not in b_location.keys() or 'coordinates' not in b_location['point'].keys():
			return None

		location = dict()
		location['formatted_address'] = b_location['address']['formattedAddress']
		location['lat'] = b_location['point']['coordinates'][0]
		location['lng'] = b_location['point']['coordinates'][1]
		return location

	def _format_nominatim_format(self, n_location):
		"""
		Extracts relevant information from nominatim result
		:param n_location:
		:return: dictionary of a location with: formatted_address, lat, lng
		"""
		if 'display_name' not in n_location.keys():
			return None
		if 'lon' not in n_location.keys():
			return None

		location = dict()
		location['formatted_address'] = n_location['display_name']
		location['lat'] = n_location['lat']
		location['lng'] = n_location['lon']
		return location

	@staticmethod
	def run_request(url, data=None, headers=None):
		"""
		This is a general method to interact with any restful API implementation.
		:param url: The url should be prepared in advance with all it's parameters (key, options, etc.)
		:param data: the data to supply to the server, case of POST requests
		:param headers: If required.
		:return: A JSON object of the results. -- Make sure you request valid JSON from the API server.
		"""
		if data and headers:
			request = urllib2.Request(url, data, headers)
		elif data:
			request = urllib2.Request(url, data)
		else:
			request = urllib2.Request(url)
		try:
			request_open = urllib2.urlopen(request)
			response = request_open.read()
			request_open.close()
			return json.loads(response)
		except urllib2.HTTPError as e:
			logger.error('%s: %s - Needs to generate new tokens', e.code, e.reason)
			return None

	def bash_geocoding(self):
		"""
		Returns the different geocoordinates of a set of locations.
		@author: Noora
		:return: a file in which each line contains the geo coordinates of a given location.
		"""

		# open location_dict
		locations = []
		location_dic_file = open('../data/location_dict.txt')
		for line in location_dic_file:
			#x = line.split(';')
			#loc = x[2].strip()
			locations.append(line.strip())
		location_dic_file.close()

		geolocated_locations_file = open('../data/geolocated_locations.txt', 'w')
		for location in locations:
			broken = location.split(',')
			location_name = broken[0]
			location_dict = dict()
			location_dict['name'] = location_name
			googleResult = self.google_geocoding_from_scratch(location_name)
			bingResult = self.bing_geocoding(location_name)
			nominatimResult = self.nominatim_geocoding(location_name)

			if bingResult is None and googleResult is None and nominatimResult is None:
				coordinatesResult = None
			else:
				coordinatesResult = {'google': googleResult, 'bing': bingResult,'nominatim': nominatimResult}

			location_dict['coordinates'] = coordinatesResult
			if (len(broken) > 1):
				broken.pop(0)
			elif(len(broken) == 1):
				broken = None
			location_dict['alternatives'] = broken
			#print location_dict
			#print json.dumps(location_dict)
			geolocated_locations_file.write(json.dumps(location_dict)+'\n')
		geolocated_locations_file.close()

	def geocode_location(self, location):
		"""
		Returns geocodes (google, bing, nominatim) of a given location.
		1. check if location has been resolved in the past, and return its geocodes
		2. Else, request online geocoding and save to file.
		:param location: a location name, String.
		:return: Json object with all geo-codes of the location.
		"""
		location = location.lower()
		if location in self.geocoded_locations.keys():
			return self.geocoded_locations[location]
		else:
			geocodes = self.request_online_geocodes(location)
			# add to the list of geocoded locations
			self.geocoded_locations[location.lower()] = geocodes
			# Sofiane: I have disabled the persister for now.
			# write into the file
			# self.persist_geocodes(geocodes)
			return geocodes

	def persist_geocodes(self, geocodes):
		f = open(self.geocoded_location_files, 'a')
		f.write(json.dumps(geocodes)+'\n')
		f.close()

	def request_online_geocodes(self, location):
		""" Returns the different geocoordinates for one location.
		@author: Sofiane
		:return: a json object with all geocoding information.
		"""

		location_dict = dict()
		location_dict['name'] = location
		location = location.encode('utf-8')
		googleResult = self.google_geocoding_from_scratch(location)
		bingResult = self.bing_geocoding(location)
		nominatimResult = self.nominatim_geocoding(location)

		if bingResult is None and googleResult is None and nominatimResult is None:
			coordinatesResult = None
		else:
			coordinatesResult = {'google': googleResult, 'bing': bingResult, 'nominatim': nominatimResult}

		location_dict['coordinates'] = coordinatesResult
		return location_dict

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
			lat = tweet['coordinates']['coordinates'][0]
			lng = tweet['coordinates']['coordinates'][1]
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
			qatar_locations = self.get_qatar_locations()
			user_location = clean_text(tweet['user']['location'].lower())
			user_locations = user_location.split()
			for usr_location in user_locations:
				if usr_location in qatar_locations:
					return True
			return False


	@staticmethod
	def get_qatar_locations():
		"""
		not used currently
		:return:
		"""
		locations = []
		with open('data/geolocated_locations.txt') as f:
			for line in f:
				if len(line.strip()) == 0:
					continue
				location = json.loads(line)
				locations.append(location['name'].lower())
		return locations

if __name__ == '__main__':
	GEOCODED_LOCATION_DICT_FILE = '../data/geolocated_locations.txt'
	GOOGLE_KEY = '[REDACTED]'
	BING_KEY = '[REDACTED]'
	GEOCODED_LOCATION_DICT_FILE = '../data/geolocated_locations.txt'
	lg = LocationGeocoding('en', google_key=GOOGLE_KEY, bing_key=BING_KEY, country_code='QA', geocoded_location_file=GEOCODED_LOCATION_DICT_FILE)
	#lg.bash_geocoding()
	#print lg.request_online_geocodes('Landmark')
	# Geocode all streets.
	# outputfile = open('../data/qatar_streets_roads_geocoded.txt', 'w')
	# streets = [w.lower() for w in open('../data/qatar_streets_roads.txt').read().split('\n')[:-1]]
	# cpt = 0
	# for st in streets:
	# 	print 'geocoding street nb: %s' % cpt
	# 	cpt += 1
	# 	x = lg.request_online_geocodes(st)
	# 	outputfile.write(json.dumps(x)+'\n')
	# outputfile.close()
