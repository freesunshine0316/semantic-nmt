import sys, os, json

amr = [x.strip() for x in open(sys.argv[1]+'_jamr.en','rU')]
print 'len(amr)', len(amr)
src = [x.strip() for x in open(sys.argv[1]+'_bpe.en','rU')]
print 'len(src)', len(src)
sent = [x.strip() for x in open(sys.argv[1]+'_bpe.de','rU')]
print 'len(sent)', len(sent)
assert len(amr) == len(src) and len(amr) == len(sent)

ids = None
if os.path.isfile(sys.argv[1]+'-ids.txt'):
    ids = [x.strip() for x in open(sys.argv[1]+'-ids.txt','rU')]
    assert len(amr) == len(ids)

data = []
for i in range(len(amr)):
    json_obj = {'amr':amr[i],'src':src[i],'sent':sent[i],}
    if ids != None:
        json_obj['id'] = ids[i]
    data.append(json_obj)
print len(data)
json.dump(data,open(sys.argv[1]+'.json_allbpe','w'))

