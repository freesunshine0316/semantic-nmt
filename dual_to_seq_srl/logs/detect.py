import sys
for i, line in enumerate(open(sys.argv[1],'rU')):
    a = line.strip().split('\t')
    if len(a) != 2:
        print i
