import json
import re
import numpy as np
import random
import padding_utils
import amr_utils
import os, psutil
import namespace_utils
from vocab_utils import Vocab

def read_text_file(text_file):
    lines = []
    with open(text_file, "rt") as f:
        for line in f:
            line = line.decode('utf-8')
            lines.append(line.strip())
    return lines

def read_amr_file(inpath, options, word_vocab_enc, word_vocab_dec, char_vocab, edgelabel_vocab):
    nodes = [] # [batch, node_num,]
    in_neigh_indices = [] # [batch, node_num, neighbor_num,]
    in_neigh_edges = []
    out_neigh_indices = [] # [batch, node_num, neighbor_num,]
    out_neigh_edges = []
    sources = [] # [batch, sent_length,]
    sentences = [] # [batch, sent_length,]
    sentences_idx = [] # [batch, sent_length,]
    ids = []
    max_in_neigh = 0
    max_out_neigh = 0
    max_node = 0
    max_sent = 0
    self_id = edgelabel_vocab.getIndex(':self')
    with open(inpath, "rU") as f:
        for id, inst in enumerate(json.load(f)):
            if id % 100000 == 0:
                process = psutil.Process(os.getpid())
                print('Memory usage after instance {}: {} GB'.format(id, process.memory_info().rss/1024/1024/1024))
            dep = inst['dep']
            src = inst['src'].strip().split()[:options.max_src_len]
            sent = inst['sent'].strip().split() # need to keep the original reference
            id = inst['id'] if inst.has_key('id') else None
            amr_node = dep['toks'] # dependency is always shorter (<=50) than threshold (80)
            if len(amr_node) > options.max_node_num:
                print('!!! longer dependency tree than threshold')
                continue
            # digitalize
            amr_node = word_vocab_enc.to_index_sequence_for_list(amr_node)
            src = word_vocab_enc.to_index_sequence_for_list(src)
            sent_idx = word_vocab_dec.to_index_sequence_for_list(sent[:options.max_answer_len-1])
            # store
            # 1.
            nodes.append(amr_node)
            # 2. & 3.
            in_indices = [[i,] for i, x in enumerate(amr_node)]
            in_edges = [[self_id,] for i, x in enumerate(amr_node)]
            out_indices = [[i,] for i, x in enumerate(amr_node)]
            out_edges = [[self_id,] for i, x in enumerate(amr_node)]
            for i, values in dep['pas'].iteritems():
                i = int(i)
                if i >= len(amr_node):
                    print('!!! i')
                    continue
                for lb, j in values:
                    if j >= len(amr_node):
                        print('!!! j')
                        continue
                    assert type(lb) == unicode or type(lb) == str
                    lb = edgelabel_vocab.getIndex(lb)
                    in_indices[j].append(i)
                    in_edges[j].append(lb)
                    out_indices[i].append(j)
                    out_edges[i].append(lb)
            in_neigh_indices.append([x[:options.max_in_neigh_num] for x in in_indices])
            in_neigh_edges.append([x[:options.max_in_neigh_num] for x in in_edges])
            out_neigh_indices.append([x[:options.max_out_neigh_num] for x in out_indices])
            out_neigh_edges.append([x[:options.max_out_neigh_num] for x in out_edges])
            # 4.
            sources.append(src)
            sentences.append(sent)
            sentences_idx.append(sent_idx)
            ids.append(id)
            # update lengths
            max_in_neigh = max(max_in_neigh, max(len(x) for x in in_indices))
            max_out_neigh = max(max_out_neigh, max(len(x) for x in out_indices))
            max_node = max(max_node, len(amr_node))
            max_sent = max(max_sent, len(sent))
    return zip(nodes, in_neigh_indices, in_neigh_edges, out_neigh_indices, out_neigh_edges, sources, sentences_idx, sentences, ids), \
            max_node, max_in_neigh, max_out_neigh, max_sent

def read_amr_from_fof(fofpath, options, word_vocab_enc, word_vocab_dec, char_vocab, edgelabel_vocab):
    all_paths = read_text_file(fofpath)
    all_instances = []
    max_node = 0
    max_in_neigh = 0
    max_out_neigh = 0
    max_sent = 0
    for cur_path in all_paths:
        print(cur_path)
        cur_instances, cur_node, cur_in_neigh, cur_out_neigh, cur_sent = read_amr_file(cur_path, options,
                word_vocab_enc, word_vocab_dec, char_vocab, edgelabel_vocab)
        all_instances.extend(cur_instances)
        max_node = max(max_node, cur_node)
        max_in_neigh = max(max_in_neigh, cur_in_neigh)
        max_out_neigh = max(max_out_neigh, cur_out_neigh)
        max_sent = max(max_sent, cur_sent)
    return all_instances, max_node, max_in_neigh, max_out_neigh, max_sent

class G2SDataStream(object):
    def __init__(self, all_instances, word_vocab_enc=None, word_vocab_dec=None, char_vocab=None, edgelabel_vocab=None, options=None,
                 isShuffle=False, isLoop=False, isSort=True, batch_size=-1):
        self.options = options
        if batch_size ==-1: batch_size=options.batch_size
        # index tokens and filter the dataset
        src_cover = 0.0
        src_total = 0.0
        node_cover = 0.0
        node_total = 0.0
        for (nodes, in_neigh_indices, in_neigh_edges, out_neigh_indices, out_neigh_edges, source, sentence_idx, sentence, id) in all_instances:
            src_cover += sum(x != word_vocab_enc.vocab_size for x in source)
            src_total += len(source)
            node_cover += sum(x != word_vocab_enc.vocab_size for x in nodes)
            node_total += len(nodes)
        if src_cover/src_total < 0.9 or node_cover/node_total < 0.9:
            print('source coverage rate: {}'.format(src_cover/src_total))
            print('node coverage rate: {}'.format(node_cover/node_total))
            print('=====')

        # sort instances based on length
        if isSort:
            all_instances = sorted(all_instances, key=lambda inst: (len(inst[0]), len(inst[5])))

        self.num_instances = len(all_instances)

        # distribute questions into different buckets
        batch_spans = padding_utils.make_batches(self.num_instances, batch_size)
        self.batches = []
        for batch_index, (batch_start, batch_end) in enumerate(batch_spans):
            cur_instances = []
            for i in xrange(batch_start, batch_end):
                cur_instances.append(all_instances[i])
            cur_batch = G2SBatch(cur_instances, options, word_vocab=word_vocab_dec)
            self.batches.append(cur_batch)

        self.num_batch = len(self.batches)
        self.index_array = np.arange(self.num_batch)
        self.isShuffle = isShuffle
        if self.isShuffle: np.random.shuffle(self.index_array)
        self.isLoop = isLoop
        self.cur_pointer = 0

    def nextBatch(self):
        if self.cur_pointer>=self.num_batch:
            if not self.isLoop: return None
            self.cur_pointer = 0
            if self.isShuffle: np.random.shuffle(self.index_array)
        cur_batch = self.batches[self.index_array[self.cur_pointer]]
        self.cur_pointer += 1
        return cur_batch

    def reset(self):
        if self.isShuffle: np.random.shuffle(self.index_array)
        self.cur_pointer = 0

    def get_num_batch(self):
        return self.num_batch

    def get_num_instance(self):
        return self.num_instances

    def get_batch(self, i):
        if i>= self.num_batch: return None
        return self.batches[i]

class G2SBatch(object):
    def __init__(self, instances, options, word_vocab=None):
        # general stuff
        self.options = options

        self.instances = instances
        self.batch_size = len(instances)
        self.vocab = word_vocab

        # create length
        self.node_num = [] # [batch_size]
        self.src_len = [] # [batch_size]
        self.sent_len = [] # [batch_size]
        for (nodes_idx, in_neigh_indices, in_neigh_edges_idx, out_neigh_indices, out_neigh_edges_idx,
                source_idx, sentence_idx, sentence, id) in instances:
            self.node_num.append(len(nodes_idx))
            self.src_len.append(len(source_idx))
            self.sent_len.append(len(sentence_idx)+1 if len(sentence_idx) < options.max_answer_len else len(sentence_idx))

        # neigh mask
        self.in_neigh_mask = [] # [batch_size, node_num, neigh_num]
        self.out_neigh_mask = []
        for instance in instances:
            ins = []
            for in_neighs in instance[1]:
                ins.append([1 for _ in in_neighs])
            self.in_neigh_mask.append(ins)
            outs = []
            for out_neighs in instance[3]:
                outs.append([1 for _ in out_neighs])
            self.out_neigh_mask.append(outs)

        # node char num
        if options.with_char:
            assert False

       # create word representation
        start_id = word_vocab.getIndex('<s>')
        end_id = word_vocab.getIndex('</s>')

        self.nodes = [x[0] for x in instances]
        self.in_neigh_indices = [x[1] for x in instances]
        self.in_neigh_edges = [x[2] for x in instances]
        self.out_neigh_indices = [x[3] for x in instances]
        self.out_neigh_edges = [x[4] for x in instances]

        self.src = []
        self.sent_inp = []
        self.sent_out = []
        for _, _, _, _, _, source_idx, sentence_idx, sentence, id in instances:
            self.src.append(source_idx)
            if len(sentence_idx) < options.max_answer_len:
                self.sent_inp.append([start_id,]+sentence_idx)
                self.sent_out.append(sentence_idx+[end_id,])
            else:
                self.sent_inp.append([start_id,]+sentence_idx[:-1])
                self.sent_out.append(sentence_idx)


class G2SBatchPadd(object):
    def __init__(self, ori_batch):
        self.options = ori_batch.options
        self.instances = ori_batch.instances
        self.batch_size = ori_batch.batch_size
        self.vocab = ori_batch.vocab

        self.node_num = np.array(ori_batch.node_num, dtype=np.int32)
        self.src_len = np.array(ori_batch.src_len, dtype=np.int32)
        self.sent_len = np.array(ori_batch.sent_len, dtype=np.int32)

        self.in_neigh_mask = padding_utils.pad_3d_vals_no_size(ori_batch.in_neigh_mask)
        self.out_neigh_mask = padding_utils.pad_3d_vals_no_size(ori_batch.out_neigh_mask)

        # making ndarray
        self.nodes = padding_utils.pad_2d_vals_no_size(ori_batch.nodes)
        if self.options.with_char:
            self.nodes_chars = padding_utils.pad_3d_vals_no_size(ori_batch.nodes_chars)
        self.in_neigh_indices = padding_utils.pad_3d_vals_no_size(ori_batch.in_neigh_indices)
        self.in_neigh_edges = padding_utils.pad_3d_vals_no_size(ori_batch.in_neigh_edges)
        self.out_neigh_indices = padding_utils.pad_3d_vals_no_size(ori_batch.out_neigh_indices)
        self.out_neigh_edges = padding_utils.pad_3d_vals_no_size(ori_batch.out_neigh_edges)

        assert self.in_neigh_mask.shape == self.in_neigh_indices.shape
        assert self.in_neigh_mask.shape == self.in_neigh_edges.shape
        assert self.out_neigh_mask.shape == self.out_neigh_indices.shape
        assert self.out_neigh_mask.shape == self.out_neigh_edges.shape

        # [batch_size, sent_len_max]
        self.src = padding_utils.pad_2d_vals(ori_batch.src, len(ori_batch.src), self.options.max_src_len)
        self.sent_inp = padding_utils.pad_2d_vals(ori_batch.sent_inp, len(ori_batch.sent_inp), self.options.max_answer_len)
        self.sent_out = padding_utils.pad_2d_vals(ori_batch.sent_out, len(ori_batch.sent_out), self.options.max_answer_len)


if __name__ == "__main__":
    FLAGS = namespace_utils.load_namespace('../config.json')
    print('Collecting vocab')
    allEdgelabels = set([line.strip().split()[0] \
            for line in open('../data/edgelabel_vocab.en', 'rU')])
    edgelabel_vocab = Vocab(voc=allEdgelabels, dim=FLAGS.edgelabel_dim, fileformat='build')
    word_vocab_enc = Vocab('../data/vectors.en.st', fileformat='txt2')
    word_vocab_dec = Vocab('../data/vectors.de.st', fileformat='txt2')
    print('Loading trainset')
    trainset, _, _, _, _ = read_amr_file('../data/newstest2013.tok.json', FLAGS,
            word_vocab_enc, word_vocab_dec, None, edgelabel_vocab)
    print('Build DataStream ... ')
    trainDataStream = G2SDataStream(trainset, word_vocab_enc, word_vocab_dec, None, edgelabel_vocab,
            options=FLAGS, isShuffle=True, isLoop=True, isSort=True)
    print('DONE!')

