__author__ = 'sofiane'
import urllib
import urllib2
from urllib2 import HTTPError
import json
import logging

logger = logging.getLogger('__name__')
class LocationGeocoding:
	def __init__(self, google_key=None, bing_key=None, country_code='QA'):
		self.google_key = google_key
		self.bing_key = bing_key
		self.country_code = country_code

	def google_geocoding(self, location):
		basepath = 'https://maps.googleapis.com/maps/api/geocode/json?'
		params = urllib.urlencode({'address': location, 'components': 'country :'+self.country_code,
								   'key': self.google_key})
		print basepath+params
		obj = self.run_request(basepath + params)
		if 'results' not in obj.keys() or len(obj['results']) == 0:
			return None
		obj = obj['results'][0]
		print json.dumps(obj)
		print self._format_google_location(obj)

	def _format_google_location(self, o):
		location = dict()
		if 'address_components' in o.keys() and len(o['address_components']) > 0:
			country = o['address_components'][-1]
			if country['short_name'] != self.country_code:
				print 'P1'
				return None

		if 'formatted_address' not in o.keys():
			print 'P2'
			return None
		location['google_formatted_address'] = o['formatted_address']

		if 'geometry' not in o.keys() or 'location' not in o['geometry'].keys()\
				or 'lat' not in o['geometry']['location'].keys():
			print 'P3'
			return None
		location['lat'] = o['geometry']['location']['lat']
		location['lng'] = o['geometry']['location']['lng']
		return location




	def run_request(self,url,data=None,headers=None):
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

gkey = '[REDACTED]'
lg = LocationGeocoding(gkey)
lg.google_geocoding('City Center shopping mall')