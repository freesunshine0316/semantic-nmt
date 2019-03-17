
import os, sys, json
import amr_utils

def stat(inpath):
    nodes = 0
    nums = 0
    with open(inpath, "rU") as f:
        for i, line in enumerate(f):
            amr = line.strip()
            amr_node = []
            amr_edge = []
            amr_utils.read_anonymized(amr.strip().split(), amr_node, amr_edge)
            nodes += len(amr_node)
            nums += 1
    print 1.0*nodes/nums

print 'nc-v11', stat('nc-v11.tok_le50_jamr.en')
print 'all', stat('all.tok_le50_jamr.en')
print 'newstest2013', stat('devtest/newstest2013.tok_jamr.en')
print 'newstest2016', stat('devtest/newstest2016.tok_jamr.en')

