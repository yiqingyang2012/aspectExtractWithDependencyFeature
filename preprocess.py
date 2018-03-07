import operator
from nltk.tag import StanfordPOSTagger
import nltk
from nltk.stem.porter import *
from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords
from pycorenlp import StanfordCoreNLP
import sys
import random
import os


reload(sys)
sys.setdefaultencoding('utf-8')

def get_lable_2(aspects, review):
    reviewLen = len(review)
    indexList = ['O']*reviewLen
    stemmer = PorterStemmer()
    min = 0
    for aspectelement in aspects:
        if len(aspectelement) < min:
            min = len(aspectelement)
    i = 0
    
    while 1:
        addlen = 1
        if i >= reviewLen:
            break
        for aspectelment in aspects:
            aspectLen = len(aspectelment)
            if i+aspectLen > reviewLen:
                continue
            aspectelment[-1] = stemmer.stem(aspectelment[-1])
            tmp = review[i:i+aspectLen]
            tmp[-1] = stemmer.stem(tmp[-1])
            if operator.eq(aspectelment,tmp):
                indexList[i] = 'B-TERM'
                addlen = aspectLen
                for j in range(1,len(aspectelment)):
                    indexList[i+j] = 'I-TERM'
                break
        i += addlen
    return indexList

'''
aspects = [['aa','bb'],['cc','dd','ee']]
review = ['aa','bb','cc','dd','ee','bb']
print get_lable_2(aspects, review)


def postag(inputSentence):
    sent_tokenize_list = sent_tokenize(inputSentence)
    print sent_tokenize_list
    tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
    sentences = sent_tokenize("the camera is very easy to use. In fact on a recent trip this past week i was asked to take a picture of a vacationing elderly group .")
    print sentences
    sentences_2 =  tokenizer.tokenize("the camera is very easy to use. In fact on a recent trip this past week i was asked to take a picture of a vacationing elderly group .")
    
    result = []
    for sentence in sentences:
        sent_tokenize_list =  nltk.word_tokenize(sentence)
        print sent_tokenize_list
        filtered = [w for w in sent_tokenize_list if w not in stopwords.words('english')]
        print filtered
        result.append(filtered)
    eng_tagger = StanfordPOSTagger('english-bidirectional-distsim.tagger')
    for sentence in result:
        print eng_tagger.tag(sentence)
    print "end"
    print eng_tagger.tag(sentences_2)

inp = "Rami Eid is studying at Stony Brook University in NY."
postag(inp)

inp = "camera[+2]##this is my first digital camera , and what a ' toy ' it is ! "

p = re.compile("(ab)?")
m = p.match("cabdabd")
print "dd"
print m.group()
print m.span()
'''

def pos_tag(review):
    eng_tagger = StanfordPOSTagger('english-bidirectional-distsim.tagger')
    tmp = eng_tagger.tag(review)
    result = []
    for element in tmp:
        result.append(element[1])
    return result

def rawfileprocess(rawfile, outputFile, aspect_file):
    f = open(rawfile)
    fout = open(outputFile, 'a')
    faspectfile = open(aspect_file, 'a')
    result = []
    aspectset = set()
    nlp = StanfordCoreNLP('http://localhost:9000')

    for line in f:
        line = line.strip()
        seperatorIndex = line.find('##')
        if seperatorIndex <= 0:
            continue

        #aspect prrprocess
        aspectString = line[:seperatorIndex].strip()
        if aspectString.find('[') < 0:
            continue
        aspectsTmp = aspectString.split(',')
        aspects = []
        for aspectScore in aspectsTmp:
            aspectScore = aspectScore.strip(' ')
            if aspectScore.find('[u]') >= 0 or aspectScore.find('[p]') >= 0:
                continue

            endIndex = aspectScore.find('[')
            if endIndex < 0:
                continue
            aspects.append(aspectScore[:endIndex].split())
            for aspectitem in aspectScore[:endIndex].split():
                if aspectitem != ' ':
                    aspectset.add(aspectitem)

        if len(aspects) == 0:
            continue

        #sentence tokenizer and word tokenizer and dep pos
        rawReview_1 = line[seperatorIndex+2:].strip()
        output3 = nlp.annotate(rawReview_1, properties={
            'annotators': 'tokenize,pos,depparse',
            'outputFormat': 'json'
            })

        for index_sentence in range(0,len(output3['sentences'])):
            subsentence = output3['sentences'][index_sentence]['tokens']
            subsentencedep = output3['sentences'][index_sentence]['enhancedPlusPlusDependencies']
            tmpword = []
            tmppos = []
            tmpdeps = []
            for index in range(0,len(subsentence)):
                tmpword.append(subsentence[index]['word'])
                tmppos.append(subsentence[index]['pos'])
                tmpdep = ''
                for deps in subsentencedep:
                    if deps['dependent'] == index+1 or deps['governor'] == index+1:
                        dependent_index = deps['dependent'] - 1
                        gov_index = deps['governor'] - 1
                        if deps['governorGloss'] == 'ROOT':
                            govpos = '#'
                        else:
                            govpos = subsentence[gov_index]['pos']

                        if deps['dependentGloss'] == 'ROOT':
                            deppos = '#'
                        else:
                            deppos = subsentence[dependent_index]['pos']

                        tmpdep += '('+deps['dep']+' '+deps['governorGloss']+' '+govpos+' '+deps['dependentGloss']+' '+deppos+')\t'
                tmpdep.strip('\t')
                tmpdeps.append(tmpdep)

            lables = get_lable_2(aspects, tmpword)
            if 'B-TERM' not in lables:
                continue

            '''
            for i in range(0,len(lables)):
                result.append(tmpword[i]+'\t'+tmppos[i] +'\t'+lables[i]+'\n') #+'\t'+tmpdeps[i]
                #result.append('\n')
            result.append('\n')
            '''
            for i in range(0,len(lables)):
                result.append(tmpword[i]+'\t'+tmppos[i] +'\t'+lables[i]+'\t'+tmpdeps[i]+'\n')
            result.append('\n')

    try:
        for aspect in aspectset:
            faspectfile.write(aspect+'\n')
        for word in result:
            fout.write(word)
    except IOError:
        print " IOError exception"
        exit(0)
    f.close()
    fout.close()
    faspectfile.close()

def listfiels(in_path, out_data_path):
    pre_out_file = out_data_path+'output.txt'
    aspect_file = out_data_path+'aspectfile'
    if os.path.exists(pre_out_file):
        os.remove(pre_out_file)
    if os.path.exists(aspect_file):
        os.remove(aspect_file)

    path = in_path.replace("\\", "/")
    mlist = os.listdir(path)
 
    for m in mlist:
        mpath = os.path.join(path, m)
        if os.path.isfile(mpath):
            pt = os.path.abspath(mpath)
            print pt
            rawfileprocess(pt, pre_out_file, aspect_file)
        else:
            pt = os.path.abspath(mpath)
            print pt
            listfiels(pt)

def splitfile(out_data_path):
    fi = open(out_data_path + '/output.txt')
    ftest = open(out_data_path + '/test.txt','w')
    ftrain = open(out_data_path + '/train.txt','w')
    ftestthree = open(out_data_path + '/testthree.txt','w')
    ftrainthree = open(out_data_path + '/trainthree.txt','w')
    lines = []
    sentence = []
    for line in fi:
        if line == '\n':
            lines.append(tuple(sentence))
            sentence= []
        else:
            sentence.append(line)

    random.shuffle(lines)
    sentence_len = len(lines)
    test_len = sentence_len/10
    test_sentence = lines[0:test_len]
    train_sentence = lines[test_len:]

    for sentence in test_sentence:
        for word in sentence:
            ftest.write(word)
            words = word.split('\t')
            ftestthree.write(words[0]+'\t'+words[1]+'\t'+words[2]+'\n')
        ftestthree.write('\n')
        ftest.write('\n')

    for sentence in train_sentence:
        for word in sentence:
            ftrain.write(word)
            words = word.split('\t')
            ftrainthree.write(words[0]+'\t'+words[1]+'\t'+words[2]+'\n')
        ftrainthree.write('\n')
        ftrain.write('\n')
    fi.close()
    ftest.close()
    ftrain.close()
    ftrainthree.close()
    ftestthree.close()

if __name__ == '__main__':
    in_path = sys.argv[1]
    out_path = sys.argv[2]
    listfiels(in_path, out_path)
    splitfile(out_path)