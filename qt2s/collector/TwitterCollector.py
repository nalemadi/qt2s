#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'sofiane'

import logging
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import json
import redis

logger = logging.getLogger(__name__)


class TwitterCollector(StreamListener):
	""" A listener handles tweets are the received from the stream.
	This is a basic listener that just prints received tweets to stdout.
	"""
	# TODO: consider collecting tweets from: MOI Qatar, Doha News, ...etc.
	def __init__(self, r_db=None, r_channel=None,r_arabic_channel=None,keyword_dict_file=None, twitter_key=None):
		if not (r_db or r_channel):
			logger.error("You should provide redis: db and channel")
			raise Exception("You should provide redis: db and channel")
		if not keyword_dict_file:
			logger.error("You should provide a path to the keywords file")
			raise Exception("You should provide a path to the keywords file")
		if not twitter_key:
			logger.error("You should provide the Twitter credentials")
			raise Exception("You should provide the Twitter credentials")

		# To create a new credentials:
		# Go to http://dev.twitter.com and create an app.
		# The consumer key and secret will be generated for you after

		self.twitter_key = twitter_key
		# self.consumer_key = '[REDACTED]'
		# self.consumer_secret = '[REDACTED]'
		# self.access_token = '[REDACTED]'
		# self.access_token_secret = '[REDACTED]'

		# Keys generated from QT2S_QCRI Twitter account.
		# self.consumer_key = '[REDACTED]'
		# self.consumer_secret = '[REDACTED]'
		# self.access_token = '[REDACTED]'
		# self.access_token_secret = '[REDACTED]'

		# Redis Initialization
		self.db = r_db
		self.redis_channel = r_channel
		self.redis_arabic_channel = r_arabic_channel
		# Initialize traffic filter.
		with open(keyword_dict_file) as f:
			self.keywords = [w.strip().decode('utf-8') for w in f.read().split('\n')[:-1]]

	@staticmethod
	def is_valid_tweet(data):
		"""
		check if a string is a valid tweet. This will discard all error messages sent by Twitter.
		# TODO: make sure we are not mishandling some serious Twitter problems such as rate limits, etc.
		:param data: a string returned by Tweepy from Twitter.
		:return: False if the data is not a tweet, True otherwise
		"""
		try:
			o = json.loads(data)
			if o['text']:
				return True
		except ValueError, e:
			return False

	def on_data(self, data):

		# push data to redis queue
		try:
			o = json.loads(data)
			if not o['text']:
				logger.warning("Tweepy returned a non Tweet object: %s", data)
			else:
				if o['lang'] == 'ar':
					self.db.rpush(self.redis_arabic_channel, data.strip())
				else:
					#TODO: decide later on whether to keep all other tweets, or to consider only english based ones.
					self.db.rpush(self.redis_channel, data.strip())
				logger.debug('TWEET: %s', data)
			return True
		except ValueError, e:
			return False

	def on_error(self, status):
		logger.error("Error in twitter listener, status: %s", status)

	def get_tweets(self):
		"""
		Listens for ever for tweets about keywords in self.keywords. Write these tweets to Redis Channel.
		:return: Tweets matching some keywords
		"""
		auth = OAuthHandler(self.twitter_key['consumer_key'], self.twitter_key['consumer_secret'])
		auth.set_access_token(self.twitter_key['access_token'], self.twitter_key['access_token_secret'])
		while True:
			print 'Reconnecting to twitter stream after disconnection'
			#logger.warning('Reconnecting to twitter stream after disconnection.')
			try:
				print 'inside try'
				sapi = Stream(auth, self)
				print 'next step'
				sapi.filter(track=self.keywords)
			except Exception as e:
				print "Something went wrong with the listener, the exception is: %s" %(e)
				#logger.error("Something went wrong with the listener, the exception is: %s", e)
				continue

if __name__ == '__main__':
	print 'test'
	TWITTER_KEY = {'consumer_key': '[REDACTED]', 'consumer_secret': '[REDACTED]', 'access_token': '[REDACTED]', 'access_token_secret': '[REDACTED]'}
	#TWITTER_KEY = {'consumer_key': 'FiFcM5LQFMsbyJcN1IqNFBSAw', 'consumer_secret': '2j96euyEVFdgboTCwLCJYgd6V5sdT7MfMTXpyWflAkn6290STR', 'access_token': '2864252562-ckJRJyw6FqrzT3rUXV6CeYNPLP41wQOvycbhODx', 'access_token_secret': '0Yn9OsrGZGAkQvwWM8lxslSUtxFaC05T10JYvMdvhb6HG'}
	KEYWORD_DICT_FILE = '../data/traffic_dict.csv'
	REDIS_DB = redis.Redis(host='localhost', port='6379')
	write_channel = '%s:%s' % ('QT2S', 'raw_tweets')
	write_channel_arabic_tweets = '%s:%s' % ('QT2S', 'raw_arabic_tweets')
	twitter_collector = TwitterCollector(r_db=REDIS_DB, r_channel=write_channel, r_arabic_channel=write_channel_arabic_tweets,
										keyword_dict_file=KEYWORD_DICT_FILE, twitter_key=TWITTER_KEY)
	twitter_collector.get_tweets()
