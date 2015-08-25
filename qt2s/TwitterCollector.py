#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'sofiane'

import logging
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import json

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
			self.keywords = [w.strip() for w in f.read().split('\n')[:-1]]

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
			logger.warning('Reconnecting to twitter stream after disconnection.')
			try:
				sapi = Stream(auth, self)
				sapi.filter(track=self.keywords)
			except Exception as e:
				logger.error("Something went wrong with the lister, the exception is: %s", e)
				continue
