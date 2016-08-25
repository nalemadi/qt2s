from math import radians, cos, sin, asin, sqrt
import urllib2, urllib, json, httplib

class geocoding():
	def __init__(self):
		self.active_key_index = int(open('active_key_index.txt','r').read())
		self.keys = open('keys.txt').read().split('\n')[:2]
		self.apikey = self.keys[self.active_key_index]

	def set_active_key_index(indx):
		self.active_key_index = indx

	@staticmethod
	#def haversine(lon1, lat1, lon2, lat2):
	def haversine(location1, location2):
		"""
		Calculate the great circle distance between two points
		on the earth (specified in decimal degrees)
		Sofiane: got it from:http://stackoverflow.com/questions/15736995/how-can-i-quickly-estimate-the-distance-between-two-latitude-longitude-points
		"""

		lat1, lon1 = location1.split(',')
		lon1 = float(lon1)
		lat1 = float(lat1)

		lat2, lon2 = location2.split(',')
		lon2 = float(lon2)
		lat2 = float(lat2)

		# convert decimal degrees to radians
		lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

		# haversine formula
		dlon = lon2 - lon1
		dlat = lat2 - lat1
		a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
		c = 2 * asin(sqrt(a))
		km = 6367 * c
		return km

	def get_direction(self, departure, arrival, departure_time=None):
		# Sofiane.abbar
		# apikey = '[REDACTED]'

		# Choufnimlih
		# apikey = 'AIzaSyB-mU9bu7oXkoAIn086asR1naAs7q5czdI'
		apikey = self.apikey
		basepath = 'https://maps.googleapis.com/maps/api/directions/json?'
		params = {'key': apikey,
				  'origin': departure,
				  'destination': arrival}
		if departure_time is not None:
			params['departure_time'] = departure_time

		url = basepath + urllib.urlencode(params)
		request = urllib2.Request(url)
		try:
			request_open = urllib2.urlopen(request)
			response = request_open.read()
			request_open.close()
			return json.loads(response)

		except urllib2.HTTPError as e:
			print 'Problem executing google direction api call'
			return None

	@staticmethod
	def get_gdistance(gDirection, type='value'):
		try:
			return str(gDirection['routes'][0]['legs'][0]['distance'][type])
		except:
			return str(-1)

	@staticmethod
	def get_gduration(gDirection, type='value'):
		try:
			return str(gDirection['routes'][0]['legs'][0]['duration'][type])
		except:
			return str(-1)

	@staticmethod
	def get_gduration_in_traffic(gDirection, type='value'):
		try:
			return str(gDirection['routes'][0]['legs'][0]['duration_in_traffic'][type])
		except:
			return str(-1)

	def get_google_metrics(self, departure, arrival):
		direction = self.get_direction(departure=departure, arrival=arrival)
		try:
			return {'distance': direction['routes'][0]['legs'][0]['distance'],
					'duration': direction['routes'][0]['legs'][0]['duration']}
		except:
			return None


if __name__ == '__main__':
	geo = geocoding()
	direction = geo.get_direction(departure='24.98502,51.549901', arrival='25.322236093,51.418447856')
	print direction
	print geo.get_gdistance(direction)
	#print geo.get_gduration(direction)
	print geo.haversine(51.549901,24.98502,51.418447856,25.322236093)



