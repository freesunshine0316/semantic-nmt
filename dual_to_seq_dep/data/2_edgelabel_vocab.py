
import json
import numpy
import sys, os, codecs
from collections import Counter

def edgelabel_vocab(inpath):
    vocab = set([':self',])
    with open(inpath, "rU") as f:
        for id, inst in enumerate(json.load(f)):
            dep = inst['dep']
            vocab.update(dep['labels'])
    return vocab


outfile = codecs.open(sys.argv[2], 'w', 'utf-8')
for x in edgelabel_vocab(sys.argv[1]):
    outfile.write(x+'\n')
outfile.close()

