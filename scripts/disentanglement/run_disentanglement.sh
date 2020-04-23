#!/bin/bash

inputs=( ../../data/pythondev/2017/merged-pythondev-help.xml \
../../data/pythondev/2018/merged-pythondev-help.xml \
../../data/pythondev/2019/merged-pythondev-help.xml \
../../data/clojurians/2017/merged-clojurians-clojure.xml \
../../data/clojurians/2018/merged-clojurians-clojure.xml \
../../data/clojurians/2019/merged-clojurians-clojure.xml \
../../data/elmlang/2017/merged-elmlang-general.xml \
../../data/elmlang/2018/merged-elmlang-general.xml \
../../data/elmlang/2019/merged-elmlang-general.xml \
../../data/elmlang/2017/merged-elmlang-beginners.xml \
../../data/elmlang/2018/merged-elmlang-beginners.xml \
../../data/elmlang/2019/merged-elmlang-beginners.xml \
../../data/racket/2017/merged-racket-general.xml \
../../data/racket/2018/merged-racket-general.xml \
../../data/racket/2019/merged-racket-general.xml
)

#in_unigrams='elsner-charniak-08-mod/data/linux-unigrams.dump'
in_unigrams='corpora/unigram.txt'

in_techwords='elsner-charniak-08-mod/data/techwords.dump'
predictions_file_name='predictions'
max_sec='1477'


export PYTHONHASHSEED=0
export PYTHONPATH=.
export PYTHONPATH=$PYTHONPATH:$PWD/elsner-charniak-08-mod
export PYTHONPATH=$PYTHONPATH:$PWD/elsner-charniak-08-mod/analysis
export PYTHONPATH=$PYTHONPATH:$PWD/elsner-charniak-08-mod/utils
export PYTHONPATH=$PYTHONPATH:$PWD/elsner-charniak-08-mod/viewer
export PATH=$PATH:$PWD/elsner-charniak-08-mod/megam_0.92


for ((i=0; i<${#inputs[@]}; i++))
do 
	echo '*** slack-specific preprocessing'
	python3 preprocessing/preprocessChat.py -o ${inputs[$i]}.pre -i ${inputs[$i]} -n preprocessing/names.txt

	echo '*** extracting features'
	rm -fR ${inputs[$i]}.dir
	python2.7 elsner-charniak-08-mod/model/classifierTest.py corpora/training.annot ${inputs[$i]}.pre $in_unigrams $in_techwords ${inputs[$i]}.dir

	if [ ! -e elsner-charniak-08-mod/megam_0.92/megam ]; then
		echo '*** using randomforest instead of megam'
		python3 randomforest/doRandomForest.py ${inputs[$i]}.dir/$max_sec
	fi

	echo '*** running greedy.py'
	python2.7 elsner-charniak-08-mod/model/greedy.py ${inputs[$i]}.pre ${inputs[$i]}.dir/$max_sec/$predictions_file_name ${inputs[$i]}.dir/$max_sec/devkeys > ${inputs[$i]}.dnt

	echo '*** reverting preprocessing'
	python3 postprocessing/revert_preprocessing.py ${inputs[$i]}.dnt ${inputs[$i]} ${inputs[$i]}.out
done	
