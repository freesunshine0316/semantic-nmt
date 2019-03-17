
import os, sys, codecs, json

vocab = [x.strip() for x in codecs.open('all.tok_le50_jamr.vocab_top40k_nofreq.en','rU','utf-8')]
aaa = .0
bbb = .0
for i,line in enumerate(codecs.open('little_prince.tok_gold.en','rU','utf-8')):
    for tok in line.strip().split():
        #if tok[0] != ':' and tok not in ('(',')',):
        if tok[0] == ':':
            aaa += 1.0
            if tok not in vocab: bbb += 1.0

print bbb/aaa

