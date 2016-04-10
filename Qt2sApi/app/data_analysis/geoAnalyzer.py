import re
import json
from datetime import datetime
import requests

class GeoAnalyzer():
	def __init__(self,collection):
		self.collection = collection

	# def regex_search(self, search):
	# 	kws = ['.*'+ks+'.*' for ks in search.strip().split(',') if ks!='']
	# 	rexExp = re.compile('|'.join(kws), re.IGNORECASE)
	# 	return rexExp

	def regex_search(self, search):
		search_word ='.*'+search+'.*'
		rexExp = re.compile('.*'+search+'.*', re.IGNORECASE)
		return rexExp

	def find_tweets_per_location(self,search, datefrom,dateto):
		""" Find tweets that contains a specific word, this later is used as a reference to  as location 
			@Output:  cursor """
		query = self.regex_search(search)
		cursor = self.collection.find({"text": {"$regex": query, "$options": "i"} } ,{'_id': False}) #For debuging.limit(10)
		return cursor


	def get_geotagged_tweets(self):
		""" Extract all the tweets with location tags
			@Output:  cursor """
		cursor  = self.collection.find({ "coordinates": {"$ne": None }}, {"_id": False}).limit(10)
		return cursor

	def near_point(self,point,radiusMeters = 10000, collection = None):
		""" Extract all the tweets near to a given point
			@Output:  cursor """
		cursor = self.collection.find( { 'coordinates': {'$near': {'$geometry': { 'type': "Point","coordinates": point}, '$maxDistance': radiusMeters } }},{"_id": False}) #.limit(2)
		return cursor


