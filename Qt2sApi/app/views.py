
import time
from flask import render_template,Response, flash, redirect, url_for, request, abort,jsonify,stream_with_context,make_response
from app import *
from utils.utils import *
from data_analysis.timeAnalyzer import *
from data_analysis.dataAnalyzer import *
from data_analysis.geoAnalyzer import *
import flask
from itertools import groupby
import json
import time
from app import COLLECTION_ENG_NON_LOCATED_TRAFFIC, COLLECTION_ENG_LOCATED_TRAFFIC
csv_data = []



timeanalyzer = TimeAnalyzer(COLLECTION_ENG_LOCATED_TRAFFIC)
dataanalyzer = DataAnalyzer(COLLECTION_ENG_LOCATED_TRAFFIC)
geoAnalyzer = GeoAnalyzer(COLLECTION_ENG_LOCATED_TRAFFIC)


@app.route('/',methods = ['GET','POST'])
def index():
	return render_template("index.html")

#curl "http://10.2.0.108:9000/api/v1/tweets/recent?count=10"
@app.route('/api/v1/tweets/recent',methods = ['GET','POST'])
def getRecentData():
	if 'count' in request.args:
		nbr_items = request.args.get('count')
		data = dataanalyzer.get_last_nitems(nbr_items)
		return jsonify({'items': list(data) })
	else:
		return jsonify({'items': [] })


@app.route('/api/v1/tweets/search',methods = ['GET','POST'])
def getDataFromToDt():
	if 'from' in request.args and 'to' in request.args:
		from_time = request.args.get('from')
		to_time = request.args.get('to')
		query = request.args.get('q', None)
		#curl "http://10.2.0.108:9000/api/v1/tweets/search?from=2016-04-08T00:00:00&to=2016-04-15T00:00:00"
		if query == None:
			data = timeanalyzer.filter_from_to(from_time,to_time)
			return jsonify({'items': list(data) })
		#curl "http://10.2.0.108:9000/api/v1/tweets/search?q=acidents&from=2016-04-08T00:00:00&to=2016-04-15T00:00:00"
		elif query != None:
			data = timeanalyzer.find_from_to(query, from_time,to_time)
			# This is to test the function 
			#assert  all(x for x in [query.lower() in x["text"].lower()  for x in list(data) ]) == True 
			return jsonify({'items': list(data) })

	elif 'since' in request.args:
		from_time = request.args.get('since')
		query = request.args.get('q', None)
		#curl "http://10.2.0.108:9000/api/v1/tweets/search?since=2016-04-08T00:00:00"
		if query == None:
			data = timeanalyzer.filter_since_dt(from_time)
			return jsonify({'items': list(data) })
		#curl "http://10.2.0.108:9000/api/v1/tweets/search?q=acidents&since=2016-04-08T00:00:00"
		elif query != None:
			data = timeanalyzer.find_since_dt(query,from_time)
			return jsonify({'items': list(data) })

	#curl "http://10.2.0.108:9000/api/v1/tweets/search?geo=1"
	elif 'geo' in request.args :
		geo = request.args.get('geo')
		if geo == '1':
			data = geoAnalyzer.get_geotagged_tweets()
			return jsonify({'items': list(data) })

	#curl "http://10.2.0.108:9000/api/v1/tweets/search?category=Accident"
	elif 'category' in request.args :
		category = request.args.get('category')
		data = dataanalyzer.get_tweets_by_keyword(category)
		return jsonify({'items': list(data) })

	#curl "http://10.2.0.108:9000/api/v1/tweets/search?location=ABCD"
	# This should be used only with worldwide dashboard 
	elif 'location' in request.args:
		location = request.args.get('location')
		data = dataanalyzer.get_tweets_by_keyword(location)
		return jsonify({'items': list(data) })

	else:
		return jsonify({'items': [] })












