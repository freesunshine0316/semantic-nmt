
import sys
import os

output_dict = {}
ref_dict = {}
for i,line in enumerate(open(sys.argv[1],'rU')):
    if i%5 == 0:
        id = line.strip()
    elif i%5 == 1:
        ref = line.strip().split()[:-1]
        ref_dict[id] = ref
    elif i%5 == 2:
        rst = line.strip().split()[:-1]
        output_dict[id] = rst

dataset_type = None
if sys.argv[1].startswith('test'):
    dataset_type = 'test'
elif sys.argv[1].startswith('dev'):
    dataset_type = 'dev'

fout = open(sys.argv[1]+'.1best','w')
fref = open(sys.argv[1]+'.ref','w')
for i,line in enumerate(open('%s-nl.txt'%dataset_type,'rU')):
    id, ref = line.strip().split('\t')
    id = id.strip()
    print >>fout, '\t'.join([id, ' '.join(output_dict[id]), ])
    print >>fref, '\t'.join([id, ref.strip(), ])
fout.close()
fref.close()


