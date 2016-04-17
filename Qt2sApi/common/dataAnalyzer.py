import re
import json
from datetime import datetime, timedelta
import pymongo



class DataAnalyzer():
	def __init__(self):
		self.collection = None


	def regex_search_multiple_words(self, search_lst):
		kws = ['.*'+ks+'.*' for ks in search_lst if ks!='']
		rexExp = re.compile('|'.join(kws), re.IGNORECASE)
		return rexExp

	def regex_search(self, search):
		search_word ='.*'+search+'.*'
		rexExp = re.compile('.*'+search+'.*', re.IGNORECASE)
		return rexExp

	def find_tweets_by_keywords(self,collection, search):
		""" by list of keywords """
		query = self.regex_search_multiple_words(search)
		cursor = collection.find({"text": {"$regex": query, "$options": "i"} } ,{'_id': False}) #For debuging.limit(10)
		return list(cursor)


	def get_last_nitems(self,collection, nbr):
		""" Get last N tweets 
			@Output:  cursor """
		cursor = collection.find({},{'_id': False}).sort([('_id',-1)]).limit( int(nbr) )
		return list(cursor)

	def get_tweets_by_keyword(self,collection , category, count):
		""" Get tweets per category
			@Output:  cursor """

		query = self.regex_search(category)
		cursor = collection.find({'$or':[{'text': {"$regex": query, "$options": "i"} }, {'category': {"$regex": query, "$options": "i"} }]} ,{'_id': False}).limit(int(count) )	
		return list(cursor)
