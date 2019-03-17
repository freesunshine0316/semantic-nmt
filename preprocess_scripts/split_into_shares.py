
import sys, os, codecs, json


data = [line.strip() for line in codecs.open('nc-v11.tok_le50.en','rb', 'utf-8')]
one_piece = 30000
shares = 8

for i in range(shares):
    st = i*one_piece
    ed = (i+1)*one_piece
    print 'generating [%d-%d)' % (st,ed)
    f = codecs.open('nc-v11.tok_le50.en_shares_v2/10K_%04d.tok'%i, 'w', 'utf-8')
    for k in range(st, ed):
        if k < len(data):
            print >>f, data[k]
    f.close()

