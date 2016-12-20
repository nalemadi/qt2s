#!/usr/bin/python
# -*- coding: UTF-8 -*-

__author__ = 'Noora'

import logging
import json
from resources.resources import clean_text
from resources.resources import clean_ar_text
from resources.resources import ngrams
from resources.resources import ar_ngrams
from collections import defaultdict

logger = logging.getLogger('__name__')

class IncidentClassifier:
	def __init__(self, categories_dictionary_file=None):
		if categories_dictionary_file is None:
			logger.error("You should provide a path to the categories dictionary file")
			raise Exception("Error: You should provide a path to the categories dictionary file")
		word_cat_label = {}
		with open(categories_dictionary_file) as f:
			for line in f:
				categories = json.loads(line)
				for cat_label, cat_definition in categories.iteritems():
					for word in cat_definition:
						word_cat_label[clean_text(word.lower())] = cat_label
		self.categories = word_cat_label
		logger.info('New Instance\n Categories considered: %s', self.categories)

	def get_tweet_category(self, text, language):
		found_categories = defaultdict(int)
		if language == 'en':
			text = clean_text(text.lower())
		elif language == 'ar':
			text = clean_ar_text(text.lower())

		for cat_word in self.categories:
			category_len = len(cat_word.split(' '))
			if language == 'en':
				ngrams_list = ngrams(text, category_len)
			elif language == 'ar':
				ngrams_list = ar_ngrams(text, category_len)
			for ngram in ngrams_list:
				if cat_word == ngram:
					found_categories[self.categories[cat_word]] += 1
		if len(found_categories) != 0:
			return sorted(found_categories, key=found_categories.get, reverse=True)[0]
		else:
			return 'Others'

"""
if __name__ == '__main__':
	incidentClassifier = IncidentClassifier(categories_dictionary_file='../data/categories_dict.txt')
	text = u"RT @al_watanQatar: سفارتنا في #ألمانيا تؤكد سلامة جميع الرعايا القطريين بعد حادث الدهس في #برلين #الوطن #الدوحة #قطر #وزارة_الخارجية https…"
	print incidentClassifier.get_tweet_category(text, 'ar')
"""