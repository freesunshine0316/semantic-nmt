
import re
import sys
import os

fout = open(sys.argv[1]+'.1best','w')
for i, line in enumerate(open(sys.argv[1],'rU')):
    line = line.strip().replace('</s>','',10)
    if i % 4 == 1:
        print >>fout, re.sub('(@@ )|(@@ ?$)', '', line)
fout.close()

os.system('/home/lsong10/ws/exp.graph_to_seq/mosesdecoder/scripts/generic/multi-bleu.perl newstest2016.tok.de < %s.1best' % sys.argv[1])
