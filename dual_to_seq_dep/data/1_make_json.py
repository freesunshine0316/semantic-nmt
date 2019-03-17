
import sys, os, json, codecs

dep = [json.loads(x.strip()) for x in open(sys.argv[1]+'_dep.en.json','rU')]
print 'len(dep)', len(dep)
src = [x.strip() for x in open(sys.argv[1]+'_bpe.en','rU')]
print 'len(src)', len(src)
sent = [x.strip() for x in open(sys.argv[1]+'_bpe.de','rU')]
print 'len(sent)', len(sent)
assert len(dep) == len(src) and len(dep) == len(sent)

ids = None
if os.path.isfile(sys.argv[1]+'-ids.txt'):
    ids = [x.strip() for x in open(sys.argv[1]+'-ids.txt','rU')]
    assert len(dep) == len(ids)

data = []
for i in range(len(dep)):
    json_obj = {'dep':dep[i],'src':src[i],'sent':sent[i],}
    if ids != None:
        json_obj['id'] = ids[i]
    data.append(json_obj)
print len(data)
json.dump(data,open(sys.argv[1]+'.json','w'))

