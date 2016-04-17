import re
import json
from datetime import datetime, timedelta
import pymongo


class TimeAnalyzer():
	def __init__(self):
		self.collection = None

	def to_datetime(self,datestr):
		return datetime.strptime(datestr,'%a %b %d %H:%M:%S +0000 %Y')

	def regex_search_multiple_words(self, search_lst):
		kws = ['.*'+ks+'.*' for ks in search_lst if ks!='']
		rexExp = re.compile('|'.join(kws), re.IGNORECASE)
		return rexExp

	def regex_search(self, search):
		search_word ='.*'+search+'.*'
		rexExp = re.compile('.*'+search+'.*', re.IGNORECASE)
		return rexExp

	def filter_from_to(self,collection, datefrom,dateto):
		""" Extract all the tweets between two given dates
			@Output:  cursor """
		startdate = datetime.strptime(datefrom,'%Y-%m-%dT%H:%M:%S')
		enddate = datetime.strptime(dateto,'%Y-%m-%dT%H:%M:%S')
		if enddate > startdate:
			cursor = collection.find({'created_at':{'$gte':startdate,'$lt':enddate} },{'_id': False})
			return list(cursor)
		else:
			cursor = collection.find({'created_at':{'$gte':enddate,'$lt':startdate } },{'_id': False})
			return list(cursor)

	def find_from_to(self,collection, search, datefrom,dateto):
		""" Find tweets that contains a specific word in a specific period
			@Output:  cursor """
		startdate = datetime.strptime(datefrom,'%Y-%m-%dT%H:%M:%S')
		enddate = datetime.strptime(dateto,'%Y-%m-%dT%H:%M:%S')
		query = self.regex_search_multiple_words(search)
		cursor = collection.find({ 'created_at':{'$gte':startdate,'$lt':enddate},"$and": [{"text": {"$regex": query, "$options": "i"}}]} ,{'_id': False}) #For debuging.limit(10)
		return list(cursor)


	def filter_since_dt(self,collection ,  datefrom):
		""" Extract all the tweets between actual date and a given date
			@Output:  cursor """
		startdate = datetime.strptime(datefrom,'%Y-%m-%dT%H:%M:%S')
		enddate = datetime.now()
		if enddate > startdate:
			cursor = collection.find({'created_at':{'$gte':startdate,'$lt':enddate} },{'_id': False})
			return list(cursor)
		else:
			cursor = collection.find({'created_at':{'$gte':startdate,'$lt':enddate} },{'_id': False})
			return list(cursor)

	def find_since_dt(self,collection,  search, datefrom):
		""" Extract all the tweets between actual date and a given date
			@Output:  cursor """
		startdate = datetime.strptime(datefrom,'%Y-%m-%dT%H:%M:%S')
		enddate = datetime.now()
		query = self.regex_search_multiple_words(search)
		if enddate > startdate:
			cursor = collection.find({'created_at':{'$gte':startdate,'$lt':enddate},"$and": [{"text": {"$regex": query, "$options": "i"}}] },{'_id': False})
			return list(cursor)
		else:
			cursor = collection.find({'created_at':{'$gte':startdate,'$lt':enddate},"$and": [{"text": {"$regex": query, "$options": "i"}}] },{'_id': False})
			return list(cursor) 





