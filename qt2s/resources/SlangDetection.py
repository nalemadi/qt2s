__author__ = 'sofiane'

import logging
import string
from nltk.tokenize import word_tokenize, sent_tokenize


logger = logging.getLogger('__name__')


class SlangDetection:
	def __init__(self, slang_dictionary_file=None):
		if slang_dictionary_file is None:
			logger.warning("No slang dictionary provided. The program will not check for bad words")
		with open(slang_dictionary_file) as f:
			self.bad_words = [w.strip().lower() for w in f.read().split('\n')[:-1]]

	def contains_bad_words(self, text):
		"""
		Check the presence of slang language in a string
		:param text: body of the tweet
		:return: list of bad words found in the input text
		"""
		text = text.lower()
		text = [w for s in sent_tokenize(text) for w in word_tokenize(s) if w not in string.punctuation]
		found_bad_words = [w for w in text if w in self.bad_words]
		return set(found_bad_words)