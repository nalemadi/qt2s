#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'sofiane'

import logging
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream

logger = logging.getLogger(__name__)


class TwitterCollector(StreamListener):
	""" A listener handles tweets are the received from the stream.
	This is a basic listener that just prints received tweets to stdout.
	"""
	def __init__(self, r_db=None, r_channel=None, keyword_dict_file=None):
		if not (r_db and r_channel):
			raise Exception("You should provide redis: db and channel")
		if not keyword_dict_file:
			raise Exception("You should provide a path to the keywords file")

		# To create a new credentials:
		# Go to http://dev.twitter.com and create an app.
		# The consumer key and secret will be generated for you after

		# TODO: generate a new keys with a customized/dedicated Twitter account for QMIC Project
		self.consumer_key = '[REDACTED]'
		self.consumer_secret = '[REDACTED]'
		self.access_token = '[REDACTED]'
		self.access_token_secret = '[REDACTED]'

		# Redis Initialization
		self.db = r_db
		self.redis_key = r_channel
		self.keywords = [w.strip() for w in open(keyword_dict_file).read().split(',')]

	def on_data(self, data):
		# push data to redis queue
		self.db.rpush(self.redis_key, data.strip())
		logger.debug('TWEET: %s', data.strip())
		return True

	def on_error(self, status):
		logger.error("Error in twitter listener: %s", status)

	def get_tweets(self):
		"""
		Listens for ever for tweets about keywords in self.keywords. Write these tweets to Redis Channel.
		:return: Tweets matching some keywords
		"""
		auth = OAuthHandler(self.consumer_key, self.consumer_secret)
		auth.set_access_token(self.access_token, self.access_token_secret)
		while True:
			try:
				sapi = Stream(auth, self)
				sapi.filter(track=self.keywords)
			except:
				logger.error("Something went wrong with the lister, but it restarted")
				continue
