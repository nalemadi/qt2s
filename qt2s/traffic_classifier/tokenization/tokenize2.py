#!/usr/bin

#from twokenize import tokenizeRawTweetText
import twokenize as tok
import sys
import re


#tok = Tokenizer(preserve_case=False)

for line in sys.stdin:
	#print line
	#tokenized = tokenizeRawTweetText(line.strip())
	tokenized = tok.tokenize(line.decode("utf-8"))
	#print tokenized
	#print " ".join( [ re.sub(r"\s",r"_",x) for x in tokenized ])
	#print " ".join( tokenized)
	print u" ".join( tokenized).encode("utf-8")


