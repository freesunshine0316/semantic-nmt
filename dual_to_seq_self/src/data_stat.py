import json
import re
import numpy as np
import random
import padding_utils
import amr_utils

def read_text_file(text_file):
    lines = []
    with open(text_file, "rt") as f:
        for line in f:
            line = line.decode('utf-8')
            lines.append(line.strip())
    return lines

def read_amr_file(inpath):
    ratio_a = 0.0
    ratio_b = 0.0
    rst = []
    with open(inpath, "rU") as f:
        for inst in json.load(f):
            amr = inst['amr']
            src = inst['src'].strip().split()
            sent = inst['sent'].strip().split()
            id = inst['id'] if inst.has_key('id') else None
            amr_node = []
            amr_edge = []
            amr_utils.read_anonymized(amr.strip().split(), amr_node, amr_edge)
            # 1.
            cur_node_num = 1.0*len(amr_node)
            if cur_node_num > 80.0:
                continue
            # 2.
            in_indices = [[i,] for i, x in enumerate(amr_node)]
            out_indices = [[i,] for i, x in enumerate(amr_node)]
            for (i,j,lb) in amr_edge:
                in_indices[j].append(i)
                out_indices[i].append(j)
            in_indices = [x[:6] for x in in_indices]
            out_indices = [x[:6] for x in out_indices]
            cur_edge_num = 1.0*sum(len(x) for x in out_indices)
            ratio_a += sum(len(x) <= 6 for x in out_indices)
            ratio_b += len(amr_node)
            # 4.
            cur_max_in_neigh = max(len(x) for x in in_indices)
            cur_max_out_neigh = max(len(x) for x in out_indices)
            rst.append((cur_node_num, cur_edge_num, cur_max_in_neigh, cur_max_out_neigh))
    rst = sorted(rst, key=lambda x:-x[1])
    print(rst[0])
    print(1.0*ratio_a/ratio_b)


if __name__ == "__main__":
    print('newstest2013')
    read_amr_file('./data/newstest2013.tok.json')
    print('newstest2016')
    read_amr_file('./data/newstest2016.tok.json')
    print('all.tok_le50')
    read_amr_file('./data/all.tok_le50.json')

