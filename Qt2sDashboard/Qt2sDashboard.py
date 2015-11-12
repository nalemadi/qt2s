#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import logging
from datetime import datetime
from collections import Counter
from resources.GoogleFusionTableAPI import FtAPI

logging.basicConfig(filename='/tmp/gft.log', \
					format = '%(levelname)s: %(module)s: %(funcName)s: %(message)s', \
					level=logging.DEBUG)
logger = logging.getLogger(__name__)


def is_from_qatar(tweet):
	"""
	This method implement different heuristics to check whether a tweet is from Qatar.
	TODO: this method should be pushed to the core of QT2S api.
	:param tweet:
	:return: a score between 0 and 1. 1 is for high confidence, 0 is for low confidence of the tweet being from Qatar.
	"""

	# 1. get dictionaries:
	qlocations = ['qatar', 'doha', 'al gharafa', 'al dafna', 'al-dafna', 'al rayyan', 'al dawha', 'al wakra', 'corniche street',
	              'souq waqif', 'toyota signal', 'najma', 'katara', 'salwa rd', 'salwa road', 'mohammed bin thani street', 'ramada', 'emiri diwan', u'الدوحة', u'الدوحه', u'قطر']
	qhashtags = ['dohatraffic', 'qatartraffic', u'زحمهـالدوحة', u'زحمةـالدوحة', 'ashghal', 'souqwaqif', 'toyotasignal']
	qmentions = ['dohatraffic', 'dohanews', 'iloveqatar','qatarliving','moi_qatarEn','ashghalqatar']

	try:
		text = tweet['text'].lower()
	except:
		text = None
	try:
		user_location = tweet['user']['location']
	except:
		user_location = None
	try:
		user_bio = tweet['user']['description']
	except:
		user_bio = None
	try:
		user_name = tweet['user']['name']
		user_screen_name = tweet['user']['screen_name']
	except:
		user_name = None
		user_screen_name = None
	try:
		geo_coordinates = tweet['geo']['coordinates']
	except:
		geo_coordinates = None

	if text:
		for token in qlocations + qhashtags + qmentions:
			if token in text:
				return 1

	if user_location and user_bio:
		for token in qlocations:
			if token in user_location or token in user_bio:
				return 1

	# TO-DO: check if coordinates are inside Qatar bounding box. @Noora Please update the if statement.
	# if geo_coordinates in 'QATAR':
		# return 1

	# iF 1 is not returned, return 0.
	return 0


def optimized_run(inputfile, K=None, customer_name=None, table_ids_file=None):
	K = K if K else 100
	customer_name = customer_name if customer_name else inputfile.split('/')[:-1]
	print 'Generation of timeline'
	f = open(inputfile)
	trends = []
	map = []
	users = []
	hashtags = []
	tweets = []
	seen = []
	print 'Parsing the file'
	corrupted_lines = 0
	for line in f:
		try:
			obj = json.loads(line)
		except ValueError:
			corrupted_lines += 1
			continue

		# TODO: Check that the tweet is from Qatar.
		if not is_from_qatar(obj):
			continue

		# timeline: divide per 1000 to remove microseconds
		if len(line) < 100:
			continue
		if 'timestamp_ms' not in obj.keys():
			continue
		trends.append(datetime.fromtimestamp(int(obj['timestamp_ms']) / 1000).strftime('%Y-%m-%d %H:%M'))

		# users
		if 'user' not in obj.keys():
			continue
		users.append(obj['user']['screen_name'])

		# hashtags
		if 'entities' not in obj.keys():
			continue
		for h in obj['entities']['hashtags']:
			hashtags.append(h['text'].lower())

		# tweets
		if 'text' not in obj.keys():
			continue
		seen.append(obj['text'])
		tweets.append(obj)

		# map
		if 'geo' not in obj.keys() and not obj['contains_traffic_locations']:
			continue
		else:
			username = obj['user']['name'].replace(',',';')
			screenname = obj['user']['screen_name']
			imageurl = obj['user']['profile_image_url_https']

			# get a photo from media:
			picture = ''
			if 'media' in obj['entities'] and len(obj['entities']['media']) > 0:
				for media in obj['entities']['media']:
					if media['type'] == 'photo':
						picture = media['media_url']
						break

			if 'geo' in obj.keys() and obj['geo']:
				marker_name = 'yellow'
				lat = str(obj['geo']['coordinates'][0])
				lng = str(obj['geo']['coordinates'][1])
			else:
				marker_name = 'red'
				# check coordinates from places identified by QT2S.
				# Pick the first location only
				location = obj['traffic_locations'][0]['coordinates']
				if not location:
					continue
				qt2s_coordinates = None
				if location['google']:
					qt2s_coordinates = location['google']
				elif location['bing']:
					qt2s_coordinates = location['bing']
				elif location['nominatim']:
					qt2s_coordinates = location['nominatim']
				else:
					# if no coordinates at all, continue
					continue
				lat = str(qt2s_coordinates['lat'])
				lng = str(qt2s_coordinates['lng'])
			tweet = obj['text'].replace('\n', '').replace(',', ';').replace('"', "'")
			if picture != '':
				marker_name = 'large_' + marker_name
			else:
				marker_name = 'small_' + marker_name
			map.append(','.join([username, screenname, imageurl, tweet, lat+' '+lng, picture, marker_name]))

	print 'There are %s corrupted lines out of %s' % (corrupted_lines, len(tweets) + corrupted_lines)

	logger.info('Generating Files')
	logger.info('\tTimeline')
	# trends
	cnt = Counter(trends)
	trends_rows = ''
	for k in sorted(cnt.keys()):
		trends_rows += k + ',' + str(cnt[k]) + '\n'

	logger.info('\tMap')
	# maps
	maps_rows = '\n'.join(map)

	# popular users
	logger.info('\tPopular Users')
	cnt = Counter(users)
	users_rows = ''
	for k, v in cnt.most_common(K):
		users_rows += k + ',' + str(v) + '\n'

	# popular hashtags
	logger.info('\tPopular Hashtags')
	cnt = Counter(hashtags)
	hashtags_rows = ''
	for k, v in cnt.most_common(K):
		hashtags_rows += k + ',' + str(v) + '\n'

	# popular tweets:
	logger.info('\tPopular Tweets')
	cnt = Counter(seen)
	tweets_rows = ''
	for k, v in cnt.most_common(K):
		# f1.write(k.encode('utf8') + '\t' + str(v)+ '\n')
		for tweet in tweets:
			if tweet['text'] == k:
				tweets_rows += tweet['user']['name'] + ',' + \
							   tweet['user']['screen_name'] + ',' + \
							   tweet['user']['profile_image_url_https'] + ',' + \
							   tweet['text'].replace('\n', '').replace(',', ';').replace('"', "'") + ',' + \
							   str(v) + '\n'
				break
	tweets_rows = tweets_rows[:-1] # removing the last empty line

	# Transfer data into fusion tables.
	logger.info("Data into Fusion tables.\n\t1.Create a fusion table for each visualization." +
				"\n\t2.Import data into the newly created fusion tables")

	fusion_tables = {}
	basepath = '[REDACTED]qt2s/Qt2sDashboard/'
	gft = FtAPI(client_secret_file=basepath+'resources/client_secrets.json', tokens_file=basepath+'resources/tokens.json')

	# CREATE TABLES IF FIRST TIME.
	if not table_ids_file:
		# create tables.
		# Timeline
		trend_schema = dict()
		trend_schema['name'] = customer_name + '_timeline'
		trend_schema['description'] = 'Timeline of the frequency of tweets about: %s' % customer_name
		trend_schema['isExportable'] = True
		trend_schema['columns'] = [{'name': 'date', 'type': 'DATETIME'}, {'name': 'freq', 'type': 'NUMBER'}]
		logger.info("Creating a table for timeline")
		response = gft.create_table(trend_schema)
		fusion_tables['timeline'] = response['tableId']
		logger.info("Timeline table Created: %s", response['tableId'])

		# Users
		users_schema = dict()
		users_schema['name'] = customer_name + '_users'
		users_schema['description'] = 'Most %s popular users tweeting about: %s' % (K, customer_name)
		users_schema['isExportable'] = True
		users_schema['columns'] = [{'name': 'user', 'type': 'STRING'}, {'name': 'freq', 'type': 'NUMBER'}]
		logger.info("Creating a table for Users")
		response = gft.create_table(users_schema)
		fusion_tables['users'] = response['tableId']
		logger.info("Users table Created: %s", response['tableId'])

		# Hashtags
		hashtags_schema = dict()
		hashtags_schema['name'] = customer_name + '_hashtags'
		hashtags_schema['description'] = 'Most %s popular hashtags in tweets about: %s' % (K, customer_name)
		hashtags_schema['isExportable'] = True
		hashtags_schema['columns'] = [{'name': 'hashtag', 'type': 'STRING'}, {'name': 'freq', 'type': 'NUMBER'}]
		logger.info("Creating a table for Hashtags")
		response = gft.create_table(hashtags_schema)
		fusion_tables['hashtags'] = response['tableId']
		logger.info('Hashtags table created: %s', response['tableId'])

		# Map
		map_schema = dict()
		map_schema['name'] = customer_name + '_map'
		map_schema['description'] = 'Geo located tweets about: %s' % customer_name
		map_schema['isExportable'] = True
		map_schema['columns'] = [{'name': 'name', 'type': 'STRING'}, {'name': 'screenname', 'type': 'STRING'},
								 {'name': 'url', 'type': 'STRING'}, {'name': 'text', 'type': 'STRING'},
								 {'name': 'loca', 'type': 'LOCATION'}, {'name': 'picture_url', 'type': 'STRING'}]
		response = gft.create_table(map_schema)
		fusion_tables['map'] = response['tableId']
		logger.info('MAP table created: %s', response['tableId'])

		# Tweets
		tweets_schema = dict()
		tweets_schema['name'] = customer_name + '_tweets'
		tweets_schema['description'] = 'Most %s popular tweets/retweets about: %s' % (K, customer_name)
		tweets_schema['isExportable'] = True
		tweets_schema['columns'] = [{'name': 'name', 'type': 'STRING'}, {'name': 'screenname', 'type': 'STRING'}, \
									{'name': 'url', 'type': 'STRING'}, {'name': 'text', 'type': 'STRING'}, \
									{'name': 'freq', 'type': 'NUMBER'}]
		response = gft.create_table(tweets_schema)
		fusion_tables['tweets'] = response['tableId']
		logger.info('Tweets table created: %s', response['tableId'])

		# Persist fusion table IDS into a file
		json.dump(fusion_tables, open(basepath+'resources/%s_tables.json' % customer_name, 'w'))

	else:
		# Get table ids from file
		fusion_tables = json.load(open(basepath+'resources/%s_tables.json' % customer_name, 'r'))

	# Trends
	logger.info('Importing TRENDS')
	res = gft.import_rows(fusion_tables['timeline'].encode('utf-8'), trends_rows)
	logger.debug('Imported %s lines.', res['numRowsReceived'])

	# Users
	logger.info('Importing USERS')
	res = gft.import_rows(fusion_tables['users'].encode('utf-8'), users_rows.encode('utf-8'))
	logger.debug('Imported %s lines.', res['numRowsReceived'])

	# Hashtags
	logger.info('Importing HASHTAGS')
	res = gft.import_rows(fusion_tables['hashtags'].encode('utf-8'), hashtags_rows.encode('utf-8'))
	logger.debug('Imported %s lines.', res['numRowsReceived'])

	# Map
	logger.info('Importing MAP Data')
	res = gft.import_rows(fusion_tables['map'].encode('utf-8'), maps_rows.encode('utf-8'))
	logger.debug('Imported %s lines.', res['numRowsReceived'])

	# Tweets
	logger.info('Importing Tweets')
	res = gft.import_rows(fusion_tables['tweets'].encode('utf-8'), tweets_rows.encode('utf-8'))
	logger.debug('Imported %s lines.', res['numRowsReceived'])



if __name__ == '__main__':
	tweets_file = '[REDACTED]qt2s/Qt2sDashboard/data/tweets_en.txt'
	# The following command reads tweets from a file, process them, and writes them into different fusion tables.
	# optimized_run(tweets_file, customer_name='QT2S_MAP', K=200, table_ids_file=True)

	# Check if we are getting all tweets from Qatar:
	# cpt = 0
	# with open(tweets_file, 'r') as f:
	# 	for line in f:
	# 		try:
	# 			obj = json.loads(line)
	# 		except ValueError:
	# 			continue
	#
	# 		if not is_from_qatar(obj):
	# 			continue
	# 		print obj['text']
	# 		cpt +=1
	# print '\n=================\nNB Tweets:%s\n=================' % cpt
