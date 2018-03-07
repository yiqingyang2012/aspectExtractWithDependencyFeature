preprocess:
	python preprocess.py ./review ./dataout

run:
	python ./absa.py -s '\t' -i ${dataset}/train.txt -o ${dataset}/train-parser.txt
	python ./absa.py -s '\t' -i ${dataset}/test.txt -o ${dataset}/test-parser.txt
	crfsuite learn -a l2sgd -p c2=2.0 -p feature.possible_transitions=1 -p feature.possible_states=1 -m model ${dataset}/train-parser.txt
	crfsuite tag -r -m model ${dataset}/test-parser.txt > ${dataset}/tagresult.txt
	paste ${dataset}/testthree.txt ${dataset}/tagresult.txt >${dataset}/combine.txt
	cat ${dataset}/combine.txt | cut -f1,2,4,5 | perl eval.pl -d "\t"

