__author__ = 'sofiane'
import urllib
import urllib2
from urllib2 import HTTPError
import json
import logging
import googlemaps
from googlemaps.exceptions import ApiError, TransportError, Timeout, HTTPError


logger = logging.getLogger('__name__')


class LocationGeocoding:
	def __init__(self, google_key=None, bing_key=None, country_code='QA'):
		self.google_key = google_key
		self.bing_key = bing_key
		self.country_code = country_code

	def google_geocoding(self, location):
		"""
		Use GoogleMaps api to geocode a location.
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
		:param location:
		:return:
		"""
		basepath = 'http://dev.virtualearth.net/REST/v1/Locations?'
		location += ' Doha Qatar'
		formattedQuery = urllib.quote(location)
		requestURL = '{}q={}&key={}'.format(basepath, formattedQuery, self.bing_key)
		#print requestURL
		obj = self.run_request(requestURL)

		if 'resourceSets' not in obj.keys():
			return None

		estimatedTotal = obj['resourceSets'][0]['estimatedTotal']
		if estimatedTotal == 0:
			return None
		results = estimatedTotal = obj['resourceSets'][0]['resources']
		if len(results) == 0:
			return None
		indx = -1
		for i, result in enumerate(results):
			address = result['address']
			if address['countryRegion'] == 'Qatar':
				indx = i
				break
		if indx == -1:
			return None
		return  self._format_bing_location(results[indx])

	def nominatim_geocoding(self, location):
		basepath = "[REDACTED_URL]     "
		params = {"addressdetails":1,"format":"json", "country":"QA", "q":location}
		response = urllib2.urlopen(basepath+urllib.urlencode(params))
		results = response.read()
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


#TODO: @Sofiane Make sure we replace this key with a applications pecific one
gkey = '[REDACTED]'
bkey = '[REDACTED]'
lg = LocationGeocoding(google_key=gkey, bing_key=bkey, country_code='QA')
#print lg.google_geocoding('City Center shopping mall')
#print lg.google_geocoding_from_scratch('City Center shopping mall')
#print lg.bing_geocoding('corniche')
print lg.nominatim_geocoding('corniche street Qatar')
