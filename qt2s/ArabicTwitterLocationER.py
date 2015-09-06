#!/usr/bin/python
# -*- coding: UTF-8 -*-

__author__ = 'noora'

class ArabicTwitterLocationER:

	def is_tweet_has_local_expressions(self, data_text):
		local_locations = ['doha', 'qatar', u'قطر', u'الدوحة', u'الدوحه']
		has_local_expressions = False
		for expression in local_locations:
			if expression in data_text:
				has_local_expressions = True
		return has_local_expressions
