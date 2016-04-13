__author__ = 'sofiane'

import string
import re
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.tokenize import RegexpTokenizer


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

def clean_ar_text(text):
	"""
	for Arabic text
	Cleans a text by removing punctuations, urls, and non ascii characters.
	This method also uses regex-based tokenizer and removes all non words from the text.
	:param text: input text
	:return: clean text
	"""
	text = re.sub(r"http\S+", "", text)
	tokenizer = RegexpTokenizer(r'\w+')
	text = [word for sent in sent_tokenize(text) for word in tokenizer.tokenize(sent) if not word.isdigit()]
	return ' '.join(text)

def getWords(text):
	"""
	clean text
	:param text: body of the tweet
	:return: list of words
	"""
	return re.compile('\w+').findall(text)

def ngrams(inputText, n):
	"""
	get contiguous sequence of n words from a given sequence of tweet text
	:param inputText:
	:param n: size of gram
	:return: get list contiguous sequence of n words from tweet text
	"""
	inputText = getWords(inputText)
	output = []
	for i in range(len(inputText)-n+1):
		g = ' '.join(inputText[i:i+n])
		output.append(g)
	return output