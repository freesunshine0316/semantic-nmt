
import os, sys, codecs, json

def process(inpath, outfile):
    print inpath
    tokens = []
    parents = []
    labels = []
    for line in codecs.open(inpath, 'rU', 'utf-8'):
        line = line.strip()
        if line == '':
            jsonstr = json.dumps({'tokens': tokens, 'parents': parents, 'labels': labels})
            outfile.write(jsonstr+'\n')
            tokens = []
            parents = []
            labels = []
        else:
            line = [x.strip() for x in line.split('\t')]
            assert len(line) >= 8, line
            tok = line[1]
            pid = int(line[6])-1
            lbl = line[7]
            tokens.append(tok)
            parents.append(pid)
            labels.append(lbl)

inpath = sys.argv[1]+'.en.deps'
outpath = sys.argv[1]+'_dep.en.json'
outfile = codecs.open(outpath, 'w', 'utf-8')
process(inpath, outfile)
outfile.close()

## for splitted shares
#prefix = sys.argv[1]
#if prefix[-1] != '/':
#    prefix = prefix + '/'
#
#outpath = sys.argv[2]
#outfile = codecs.open(outpath, 'w', 'utf-8')
#
#i = 0
#inpath = prefix + '10K_%04d.tok.deps'%i
#while os.path.isfile(inpath):
#    process(inpath, outfile)
#    i += 1
#    inpath = prefix + '10K_%04d.tok.deps'%i
#outfile.close()
