#!/usr/bin

from happyfuntokenizing import Tokenizer
import sys
import re


tok = Tokenizer(preserve_case=False)

for line in sys.stdin:
	#print line
	tokenized = tok.tokenize(line.strip())
	#print tokenized
	print " ".join( [ re.sub(r"\s",r"_",x) for x in tokenized ])

