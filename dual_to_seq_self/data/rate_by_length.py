
import os, sys

thres = int(sys.argv[2])
right = 0.0
total = 0.0
for line in open(sys.argv[1],'rU'):
    if len(line.strip().split()) <= thres:
        right += 1.0
    total += 1.0

print right/total
