
import os, sys, json


def find_head_id(ptag, ctags, rules):
    if ptag not in rules:
        return len(ctags)-1
    for d, r in rules[ptag]:
        a,b,c = (0,len(ctags),1) if d == 'r' else (len(ctags)-1,-1,-1)
        for i in range(a,b,c):
            if len(r) == 0 or ctags[i] in r:
                return i
    return len(ctags)-1


def search_head_recur(toklst, rules):
    assert toklst[0] == '(' and toklst[-1] == ')', toklst
    if len(toklst) <= 4: # ( NP xx )
        return toklst[1], 0, 1

    assert toklst[2] == '('
    ptag = toklst[1]
    ct = 0
    children = []
    children_tags = []
    for i in range(2, len(toklst)-1):
        if toklst[i] == '(':
            ct += 1
            if ct == 1: st = i
        if toklst[i] == ')':
            ct -= 1
            if ct == 0:
                ed = i
                tag, head, length = search_head_recur(toklst[st: ed+1], rules)
                children.append((tag, head, length))
                children_tags.append(tag)
    hid = find_head_id(ptag, children_tags, rules)
    #print ptag
    #print children
    #print hid
    #print '--------'
    head = sum(children[i][2] for i in range(hid)) + children[hid][1]
    length = sum(x[2] for x in children)
    assert head < length
    return ptag, head, length


def search_head(line, rules):
    line = line.replace('(', ' ( ', 1000)
    line = line.replace(')', ' ) ', 1000)
    line = line.split()
    tag, head, length = search_head_recur(line, rules)
    #print ' '.join(line)
    #print tag, head, length
    #print '====='
    return head, length


def load_head_rules(path):
    head_rules = {}
    for line in open(path, 'rU'):
        a, b = line.strip().split('@@ ')
        a = a.strip()
        head_rules[a] = []
        for group in b.strip().split(';'):
            c = group.split()
            d, r = c[0], set(c[1:])
            head_rules[a].append((d,r))
    return head_rules


head_rules = load_head_rules('srl_to_head.rules')

fout = open(sys.argv[2], 'w')
for line in open(sys.argv[1], 'rU'):
    inst = json.loads(line.strip())
    toks = inst['toks'].split()
    pas = {}
    for srl in inst['srl']:
        prd = srl['predicate']
        prd_parse = prd['parse']
        prd_st = prd['tok_begin']
        prd_ed = prd['tok_end']
        prd_hd, prd_len = search_head(prd_parse, head_rules)
        prd_hd = prd_hd + prd_st
        print('{} {} {} {}'.format(prd_len, prd_st, prd_ed+1, len(toks)))
        assert prd_len == prd_ed+1-prd_st
        pas[prd_hd] = []
        for arg in srl['args']:
            label = arg['name']
            arg_parse = arg['arg']['parse']
            arg_st = arg['arg']['tok_begin']
            arg_ed = arg['arg']['tok_end']
            arg_hd, arg_len = search_head(arg_parse, head_rules)
            arg_hd = arg_hd + arg_st
            assert arg_len == arg_ed+1-arg_st
            pas[prd_hd].append((label, arg_hd))
    jsonstr = json.dumps({'toks':toks,'pas':pas})
    fout.write(jsonstr+'\n')
fout.close()
