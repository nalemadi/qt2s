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
		with open(keyword_dict_file) as f:
			self.keywords = [w.strip() for w in f.read().split(',')]

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
		if self.is_valid_tweet(data):
			self.db.rpush(self.redis_key, data.strip())
			logger.debug('TWEET: %s', data)
		else:
			logger.warning("Tweepy returned a non Tweet object: %s", data)
		return True

	def on_error(self, status):
		logger.error("Error in twitter listener, status: %s", status)

	def get_tweets(self):
		"""
		Listens for ever for tweets about keywords in self.keywords. Write these tweets to Redis Channel.
		:return: Tweets matching some keywords
		"""
		auth = OAuthHandler(self.consumer_key, self.consumer_secret)
		auth.set_access_token(self.access_token, self.access_token_secret)
		while True:
			logger.warning('Reconnecting to twitter stream after disconnection.')
			try:
				sapi = Stream(auth, self)
				sapi.filter(track=self.keywords)
			except Exception as e:
				logger.error("Something went wrong with the lister, the exception is: %s", e)
				continue
