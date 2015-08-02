__author__ = 'sofiane'

import string
import re
from nltk.tokenize import word_tokenize, sent_tokenize


def clean_text(text):
	"""
	Cleans a text by removing punctuations, urls, and non ascii characters.
	:param text: input text
	:return: clean text
	"""
	#TODO: to careful on the cleaning. Remove urls, #, @, and other punctuation characters.
	# 1. remove urls
	text = re.sub(r"http\S+", "", text)

	# 2. tokenize and remove punctuations: !"#$%&'()*+,-./:;<=>?@[\]^_`{|}~
	text = ' '.join([w for s in sent_tokenize(text) for w in word_tokenize(s) if w not in string.punctuation])

	# TODO: make sure we want to keep this one - 3. remove non ascii characters
	#text = ''.join([c for c in text if c in string.printable])
	return text
