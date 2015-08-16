
import json
import sys
import re


def processfile(jfile):


	file= open(jfile)
	#data = json.load(file)

	for item in file:
		data=json.loads(item)
		text=data["text"].encode("utf-8")
		text=re.sub(r"\n",". ",text)
		print text#,"\t",data["Javier"]
		#print re.sub(r"\n"," \\n ",data["text"].encode("utf-8")),"\t",data["Koushik"]		
		#print re.sub(r"\n"," \\n ",data["text"].encode("utf-8")),"\t",data["Noora"]		
		
		#for k,v in data.iteritems():
		#	print k , v

		#exit(-1)




if __name__ == '__main__':
	if len(sys.argv) >1:
		processfile(sys.argv[1])
	else:
		processfile("../data/annotated_collection_with_ids.json")
