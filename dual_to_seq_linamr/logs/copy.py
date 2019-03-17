
import os, sys

if len(sys.argv) != 3:
    print 'this src tgt'
    sys.exit(0)

os.system('cp -f G2S.%s.best.model.data-00000-of-00001 G2S.%s.best.model.data-00000-of-00001'%(sys.argv[1],sys.argv[2]))
os.system('cp -f G2S.%s.best.model.index G2S.%s.best.model.index'%(sys.argv[1],sys.argv[2]))
os.system('cp -f G2S.%s.best.model.meta G2S.%s.best.model.meta'%(sys.argv[1],sys.argv[2]))
os.system('cp -f G2S.%s.config.json G2S.%s.config.json'%(sys.argv[1],sys.argv[2]))
os.system('cp -f G2S.%s.log G2S.%s.log'%(sys.argv[1],sys.argv[2]))
os.system('cp -f G2S.%s.nodetype_vocab G2S.%s.nodetype_vocab'%(sys.argv[1],sys.argv[2]))
os.system('cp -f G2S.%s.edgelabel_vocab G2S.%s.edgelabel_vocab'%(sys.argv[1],sys.argv[2]))
os.system('cp -f G2S.%s.char_vocab G2S.%s.char_vocab'%(sys.argv[1],sys.argv[2]))

