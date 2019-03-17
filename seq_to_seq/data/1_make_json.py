import sys, os, json
import os.path

def make_annotation(lst):
    POSs = ' '.join(['P' for x in lst])
    NERs = ' '.join(['N' for x in lst])
    positions = ' '.join(['%d-0-0'%i for i in range(len(lst))])
    return POSs, NERs, positions

amr = [x.strip() for x in open(sys.argv[1]+'.en','rU')]
print 'len(amr)', len(amr)
sent = [x.strip() for x in open(sys.argv[1]+'.de','rU')]
print 'len(sent)', len(sent)
assert len(amr) == len(sent)
ids = None
if os.path.isfile(sys.argv[1]+'-ids.txt'):
    ids = [x.strip() for x in open(sys.argv[1]+'-ids.txt','rU')]
    assert len(amr) == len(ids)

data = []
for i in range(len(amr)):
    json_obj = {}
    amr_list = amr[i].strip().split()
    #amr_POSs, amr_NERs, amr_positions = make_annotation(amr_list)
    json_obj['text1'] = amr[i]
    #json_obj['annotation1'] = {'toks':amr[i], } #'POSs':amr_POSs, 'NERs':amr_NERs, 'positions':amr_positions,}
    sent_list = sent[i].strip().split()
    #sent_POSs, sent_NERs, sent_positions = make_annotation(sent_list)
    json_obj['text2'] = sent[i]
    #json_obj['annotation2'] = {'toks':sent[i], } #'POSs':sent_POSs, 'NERs':sent_NERs, 'positions':sent_positions,}
    data.append(json_obj)
    if ids != None:
        json_obj['id'] = ids[i]
    if i%100000 == 0 and i != 0:
        print i
json.dump(data,open(sys.argv[1]+'.json','w'))

