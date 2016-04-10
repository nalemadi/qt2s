import re
import json
from datetime import datetime, timedelta
import pymongo



class DataAnalyzer():
	def __init__(self,collection):
		self.collection = collection

	def regex_search(self, search):
		search_word ='.*'+search+'.*'
		rexExp = re.compile('.*'+search+'.*', re.IGNORECASE)
		return rexExp

	def get_last_nitems(self,nbr):
		""" Get last N tweets 
			@Output:  cursor """
		cursor = self.collection.find({},{'_id': False}).sort([('_id',-1)]).limit( int(nbr) )
		return cursor

	def get_tweets_by_keyword(self,category):
		""" Get tweets per category
			@Output:  cursor """

		query = self.regex_search(category)
		cursor = self.collection.find({'$or':[{'text': {"$regex": query, "$options": "i"} }, {'category': {"$regex": query, "$options": "i"} }]} ,{'_id': False})	
		return cursor

	# def get_tweets_by_keyword(self,category):
	# 	""" Get tweets per category
	# 		@Output:  cursor """

	# 	query = self.regex_search(category)
	# 	cursor = self.collection.find({"text": {"$regex": query, "$options": "i"}, "$or": [{"category": {"$regex": query, "$options": "i"}}]   } ,{'_id': False})	
	# 	return cursor