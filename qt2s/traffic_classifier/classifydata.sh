#!/bin/bash
# classifyTraffic.sh
# - Gets a  file in json format
# - returns a file with the labels for each of the instances.
# Francisco Guzman
# (c) Qatar Computing Research Institute, 2015.
#
# V.01 Works in offline mode with Stanford Classifier and some perl scripts


#STANFORD_CLASSIFIER_JAR=stanford-classifier-2015-04-20/stanford-classifier.jar
current_dir="$(dirname "$0")"
STANFORD_CLASSIFIER_JAR="$current_dir/stanford-classifier-2014-08-27/stanford-classifier.jar"
EXTRACT="$current_dir/scripts/processdata.py"
TOK="$current_dir/tokenization/tokenize2.py" # Uses CMU ARK tokenizer
SIMP="$current_dir/scripts/preprocess.pl" # my simplifier to substitute some news outlets and other events for tags.


function usage()
{
	echo "$0 jsontweetfile.json"
	exit
}

#check that we are given a file
if [ $# -lt 1 ]
	then 
	echo "Not enough parameters"
	usage
fi

#check that it is a file
if [ ! -f $1 ]
	then
	echo "First argument should be a (json) file "
	usage
fi

myfile=$1

#echo "1. Extracting tweets"
python $EXTRACT $myfile > $myfile.data || exit -1

#echo "2. Getting text"
cut -f1 $myfile.data > $myfile.data.text || exit -1

#echo "3. Tokenizing"
python $TOK < $myfile.data.text > $myfile.data.text.tok || exit -1

#echo "4. Simplifiying"
perl $SIMP < $myfile.data.text.tok > $myfile.data.text.tok.simp

#echo "5. Composing data"
paste <(cat $myfile.data.text.tok| awk '{print "-" }') $myfile.data.text.tok $myfile.data.text.tok.simp > $myfile.data.set

#echo "6. Testing"
java -mx1800m -cp $STANFORD_CLASSIFIER_JAR edu.stanford.nlp.classify.ColumnDataClassifier -loadClassifier $current_dir/data/traffic.model  -testFile $myfile.data.set  2> /dev/null | cut -f3 > $myfile.classification.results

#echo " Results are in $myfile.data.set.results"
rm -f $myfile.data*

 
