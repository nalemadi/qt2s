import re

class GeoAnalyzer():
	def __init__(self):
		self.collection = None

	def regex_search(self, search):
		search_word ='.*'+search+'.*'
		rexExp = re.compile('.*'+search+'.*', re.IGNORECASE)
		return rexExp

	def find_tweets_per_location(self,collection , search, datefrom,dateto):
		""" Find tweets that contains a specific word, this later is used as a reference to  as location 
			@Output:  cursor """
		query = self.regex_search(search)
		cursor = collection.find({"text": {"$regex": query, "$options": "i"} } ,{'_id': False}) #For debuging.limit(10)
		return list(cursor)




	def get_geotagged_tweets(self,collection ):
		""" Extract all the tweets with location tags
			@Output:  cursor """
		cursor  = collection.find({ "coordinates": {"$ne": None }}, {"_id": False}).limit(10)
		return list(cursor)

	def near_point(self,collection , point,radiusMeters = 10000):
		""" Extract all the tweets near to a given point
			@Output:  cursor """
		cursor = collection.find( { 'coordinates': {'$near': {'$geometry': { 'type': "Point","coordinates": point}, '$maxDistance': radiusMeters } }},{"_id": False}) #.limit(2)
		return list(cursor)


