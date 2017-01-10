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
						if any(x in text for x in expressions) == False and self.is_tweet_from_qatar(tweet) == False:
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
	#tweet = '{"contributors":null,"truncated":false,"text":"traffic at the mall","in_reply_to_status_id":null,"id":560824022645346300,"favorite_count":0,"retweeted":false,"coordinates":{"type":"Point","coordinates":[51.523234,25.297208]},"timestamp_ms":"1422545841262","entities":{"user_mentions":[],"media":[{"expanded_url":"http://twitter.com/AhmdAbuzied/status/560824022645346304/photo/1","sizes":{"small":{"h":603,"resize":"fit","w":340},"large":{"h":1818,"resize":"fit","w":1024},"medium":{"h":1065,"resize":"fit","w":600},"thumb":{"h":150,"resize":"crop","w":150}},"url":"http://t.co/LqK4bJrWGL","media_url_https":"https://pbs.twimg.com/media/B8hyeiSIIAEnWdI.jpg","display_url":"pic.twitter.com/LqK4bJrWGL","id_str":"560824022532104193","indices":[93,115],"type":"photo","id":560824022532104200,"media_url":"http://pbs.twimg.com/media/B8hyeiSIIAEnWdI.jpg"}],"hashtags":[{"indices":[35,47],"text":"dohatraffic"}],"symbols":[],"trends":[],"urls":[{"indices":[69,92],"url":"https://t.co/ahQhBrvF46","expanded_url":"https://www.swarmapp.com/c/39onhxZL08e","display_url":"swarmapp.com/c/39onhxZL08e"}]},"in_reply_to_screen_name":null,"in_reply_to_user_id":null,"retweet_count":0,"id_str":"560824022645346304","favorited":false,"user":{"follow_request_sent":null,"profile_use_background_image":true,"id":190063189,"verified":false,"profile_image_url_https":"https://pbs.twimg.com/profile_images/557195223185362944/LYMBVlsG_normal.jpeg","profile_sidebar_fill_color":"252429","is_translator":false,"profile_text_color":"CEEBE8","followers_count":12856,"protected":false,"location":"Cairo/Doha","default_profile_image":false,"id_str":"190063189","utc_offset":10800,"statuses_count":9492,"description":"Direct your thoughts control your emotions, and ordain your destiny.Translator cum #Marketer, #sales, #socialmedia & #photography.","friends_count":10078,"profile_background_image_url_https":"https://pbs.twimg.com/profile_background_images/602977828/awlgq9ku1fyisljxslnx.jpeg","profile_link_color":"0E89F5","profile_image_url":"http://pbs.twimg.com/profile_images/557195223185362944/LYMBVlsG_normal.jpeg","notifications":null,"geo_enabled":true,"profile_background_color":"080808","profile_banner_url":"https://pbs.twimg.com/profile_banners/190063189/1394493587","profile_background_image_url":"http://pbs.twimg.com/profile_background_images/602977828/awlgq9ku1fyisljxslnx.jpeg","screen_name":"AhmdAbuzied","lang":"en","profile_background_tile":false,"favourites_count":407,"name":"أحمد أبوزيد","url":"http://about.me/ahmadabuzied","created_at":"Mon Sep 13 00:13:28 +0000 2010","contributors_enabled":false,"time_zone":"Kuwait","profile_sidebar_border_color":"000000","default_profile":false,"following":null,"listed_count":23},"geo":{"type":"Point","coordinates":[25.297208,51.523234]},"in_reply_to_user_id_str":null,"possibly_sensitive":false,"lang":"en","created_at":"Thu Jan 29 15:37:21 +0000 2015","filter_level":"low","in_reply_to_status_id_str":null,"place":{"full_name":"Qatar","name":"Qatar","url":"https://api.twitter.com/1.1/geo/id/a54c21f6aedb2967.json","country":"دولة قطر","place_type":"country","bounding_box":{"type":"Polygon","coordinates":[[[50.7500758,24.5563659],[50.7500758,26.1828978],[51.630581,26.1828978],[51.630581,24.5563659]]]},"country_code":"QA","attributes":{},"id":"a54c21f6aedb2967"},"extended_entities":{"media":[{"expanded_url":"http://twitter.com/AhmdAbuzied/status/560824022645346304/photo/1","sizes":{"small":{"h":603,"resize":"fit","w":340},"large":{"h":1818,"resize":"fit","w":1024},"medium":{"h":1065,"resize":"fit","w":600},"thumb":{"h":150,"resize":"crop","w":150}},"url":"http://t.co/LqK4bJrWGL","media_url_https":"https://pbs.twimg.com/media/B8hyeiSIIAEnWdI.jpg","display_url":"pic.twitter.com/LqK4bJrWGL","id_str":"560824022532104193","indices":[93,115],"type":"photo","id":560824022532104200,"media_url":"http://pbs.twimg.com/media/B8hyeiSIIAEnWdI.jpg"}]}}'
	tweet = '{"contributors":null,"truncated":false,"text":"traffic at the mall and corniche qatar","in_reply_to_status_id":null,"id":560824022645346300,"favorite_count":0,"retweeted":false, "coordinates":null,"timestamp_ms":"1422545841262","entities":{"user_mentions":[],"media":[{"expanded_url":"http://twitter.com/AhmdAbuzied/status/560824022645346304/photo/1","sizes":{"small":{"h":603,"resize":"fit","w":340},"large":{"h":1818,"resize":"fit","w":1024},"medium":{"h":1065,"resize":"fit","w":600},"thumb":{"h":150,"resize":"crop","w":150}},"url":"http://t.co/LqK4bJrWGL","media_url_https":"https://pbs.twimg.com/media/B8hyeiSIIAEnWdI.jpg","display_url":"pic.twitter.com/LqK4bJrWGL","id_str":"560824022532104193","indices":[93,115],"type":"photo","id":560824022532104200,"media_url":"http://pbs.twimg.com/media/B8hyeiSIIAEnWdI.jpg"}],"hashtags":[{"indices":[35,47],"text":"dohatraffic"}],"symbols":[],"trends":[],"urls":[{"indices":[69,92],"url":"https://t.co/ahQhBrvF46","expanded_url":"https://www.swarmapp.com/c/39onhxZL08e","display_url":"swarmapp.com/c/39onhxZL08e"}]},"in_reply_to_screen_name":null,"in_reply_to_user_id":null,"retweet_count":0,"id_str":"560824022645346304","favorited":false,"user":{"follow_request_sent":null,"profile_use_background_image":true,"id":190063189,"verified":false,"profile_image_url_https":"https://pbs.twimg.com/profile_images/557195223185362944/LYMBVlsG_normal.jpeg","profile_sidebar_fill_color":"252429","is_translator":false,"profile_text_color":"CEEBE8","followers_count":12856,"protected":false,"location":"Cairo/Doha","default_profile_image":false,"id_str":"190063189","utc_offset":10800,"statuses_count":9492,"description":"Direct your thoughts control your emotions, and ordain your destiny.Translator cum #Marketer, #sales, #socialmedia & #photography.","friends_count":10078,"profile_background_image_url_https":"https://pbs.twimg.com/profile_background_images/602977828/awlgq9ku1fyisljxslnx.jpeg","profile_link_color":"0E89F5","profile_image_url":"http://pbs.twimg.com/profile_images/557195223185362944/LYMBVlsG_normal.jpeg","notifications":null,"geo_enabled":true,"profile_background_color":"080808","profile_banner_url":"https://pbs.twimg.com/profile_banners/190063189/1394493587","profile_background_image_url":"http://pbs.twimg.com/profile_background_images/602977828/awlgq9ku1fyisljxslnx.jpeg","screen_name":"AhmdAbuzied","lang":"en","profile_background_tile":false,"favourites_count":407,"name":"أحمد أبوزيد","url":"http://about.me/ahmadabuzied","created_at":"Mon Sep 13 00:13:28 +0000 2010","contributors_enabled":false,"time_zone":"Kuwait","profile_sidebar_border_color":"000000","default_profile":false,"following":null,"listed_count":23},"geo":{"type":"Point","coordinates":[25.297208,51.523234]},"in_reply_to_user_id_str":null,"possibly_sensitive":false,"lang":"en","created_at":"Thu Jan 29 15:37:21 +0000 2015","filter_level":"low","in_reply_to_status_id_str":null,"place":{"full_name":"Qatar","name":"Qatar","url":"https://api.twitter.com/1.1/geo/id/a54c21f6aedb2967.json","country":"دولة قطر","place_type":"country","bounding_box":{"type":"Polygon","coordinates":[[[50.7500758,24.5563659],[50.7500758,26.1828978],[51.630581,26.1828978],[51.630581,24.5563659]]]},"country_code":"QA","attributes":{},"id":"a54c21f6aedb2967"},"extended_entities":{"media":[{"expanded_url":"http://twitter.com/AhmdAbuzied/status/560824022645346304/photo/1","sizes":{"small":{"h":603,"resize":"fit","w":340},"large":{"h":1818,"resize":"fit","w":1024},"medium":{"h":1065,"resize":"fit","w":600},"thumb":{"h":150,"resize":"crop","w":150}},"url":"http://t.co/LqK4bJrWGL","media_url_https":"https://pbs.twimg.com/media/B8hyeiSIIAEnWdI.jpg","display_url":"pic.twitter.com/LqK4bJrWGL","id_str":"560824022532104193","indices":[93,115],"type":"photo","id":560824022532104200,"media_url":"http://pbs.twimg.com/media/B8hyeiSIIAEnWdI.jpg"}]}}'
	tweet_json = json.loads(tweet)
	print twitterLocationER.find_locations(tweet_json)
"""