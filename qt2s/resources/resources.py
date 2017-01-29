#!/usr/bin/python
# -*- coding: UTF-8 -*-

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

def getARWords(text):
	#return re.compile(r'\w+').findall(text)
	#return (re.sub(r'[a-zA-Z?]', '', text).strip())
	return re.findall(ur'[\u0600-\u06FF]+', text)

def ar_ngrams(inputText, n):
	"""
	get contiguous sequence of n words from a given sequence of tweet text
	:param inputText:
	:param n: size of gram
	:return: get list contiguous sequence of n words from tweet text
	"""
	inputText = getARWords(inputText)
	output = []
	for i in range(len(inputText)-n+1):
		g = ' '.join(inputText[i:i+n])
		output.append(g)
	return output

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

def get_blacklisted_locations():
	list = []
	with open('[REDACTED]/qt2s/qt2s/data/black_listed_locations.txt') as f:
		for line in f:
			strip_line = line.strip()
			bl_location = strip_line.lower()
			if bl_location == '':
				print 'bl_location:', bl_location
			else:
				list.append(bl_location)
	return list

def get_ar_blacklisted_locations():
	list = []
	with open('[REDACTED]/qt2s/qt2s/data/black_listed_locations_ar.txt') as f:
		for line in f:
			strip_line = line.strip()
			bl_location = strip_line.lower()
			list.append(bl_location)
	return list


def has_black_listed_location(text):
	"""
	check whether tweet text has a blacklisted location
	:param text:
	:return: boolean value
	"""
	text = text.lower()
	blacklisted_locations = get_blacklisted_locations()
	for bl_location in blacklisted_locations:
		if bl_location in text:
			print 'black location found:',bl_location
			return True
	return False

def has_ar_blacklisted_location(text):
	ar_blacklisted_locations = get_ar_blacklisted_locations()
	for ar_bl in ar_blacklisted_locations:
		if ar_bl in text.encode('utf-8'):
			return True
	return False
"""
if __name__ == '__main__':
	#ar_text = ur'زحمة في اللؤلؤة'
	#print has_ar_blacklisted_location(ar_text)
	en_text = 'this is a test for black listed locations prai'
	print has_black_listed_location(en_text)
"""