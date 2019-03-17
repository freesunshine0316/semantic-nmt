
import os, sys, codecs, json

thres = int(sys.argv[2])
aaa = .0
bbb = .0
for i,line in enumerate(codecs.open(sys.argv[1],'rU')):
    k,v = line.strip().split()
    if i < thres:
        aaa += int(v)
    bbb += int(v)

print aaa/bbb

