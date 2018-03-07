#make preprocess

make run dataset=$1> log.txt
tail -14 log.txt
