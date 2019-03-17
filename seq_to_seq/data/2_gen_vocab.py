
import json
import sys
import cPickle
import re
from collections import Counter
import codecs

def update(l, v):
    v.update([x for x in l])

def update_vocab(path, vocab_en, vocab_de, is_lower=False):
    words_en = []
    words_de = []
    data = json.load(open(path,'rU'))
    for inst in data:
        words_en = inst['text1'].strip().split()
        words_de = inst['text2'].strip().split()
        if is_lower:
            words_en = [x.lower() for x in words_en]
            words_de = [x.lower() for x in words_de]
        update(words_en, vocab_en)
        update(words_de, vocab_de)

def output(d, path):
    f = codecs.open(path,'w',encoding='utf-8')
    for k,v in sorted(d.items(), key=lambda x:-x[1]):
        print >>f, k
    f.close()

##################

vocab_en = Counter()
vocab_de = Counter()
update_vocab('all.tok_le50_bpe.json', vocab_en, vocab_de)
update_vocab('newstest2013.tok_allbpe.json', vocab_en, vocab_de)
update_vocab('newstest2014.tok_allbpe.json', vocab_en, vocab_de)
update_vocab('newstest2015.tok_allbpe.json', vocab_en, vocab_de)
update_vocab('newstest2016.tok_allbpe.json', vocab_en, vocab_de)
print len(vocab_en), len(vocab_de)

output(vocab_en, 'vocab_en.txt')
output(vocab_de, 'vocab_de.txt')

