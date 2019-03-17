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
    linamrs = [] # [batch, linamr_length,]
    sources = [] # [batch, sent_length,]
    sentences = [] # [batch, sent_length,]
    ids = []
    max_linamr = 0
    max_src = 0
    max_sent = 0
    with open(inpath, "rU") as f:
        for inst in json.load(f):
            linamr = inst['amr'].strip().split()
            src = inst['src'].strip().split()
            sent = inst['sent'].strip().split()
            id = inst['id'] if inst.has_key('id') else None
            linamrs.append(linamr)
            sources.append(src)
            sentences.append(sent)
            ids.append(id)
            # update lengths
            max_linamr = max(max_linamr, len(linamr))
            max_src = max(max_src, len(src))
            max_sent = max(max_sent, len(sent))
    return zip(linamrs, sources, sentences, ids), max_linamr, max_src, max_sent

def read_amr_from_fof(fofpath):
    all_paths = read_text_file(fofpath)
    all_instances = []
    max_linamr = 0
    max_src = 0
    max_sent = 0
    for cur_path in all_paths:
        print(cur_path)
        cur_instances, cur_linamr, cur_src, cur_sent = read_amr_file(cur_path)
        all_instances.extend(cur_instances)
        max_linamr = max(max_linamr, cur_linamr)
        max_src = max(max_src, cur_src)
        max_sent = max(max_sent, cur_sent)
    return all_instances, max_linamr, max_src, max_sent

def collect_vocabs(all_instances):
    all_words = set()
    all_chars = set()
    # nodes: [corpus_size,node_num,]
    # neigh_indices & neigh_edges: [corpus_size,node_num,neigh_num,]
    # sentence: [corpus_size,sent_len,]
    for (linamr, source, sentence, id) in all_instances:
        all_words.update(linamr)
        all_words.update(source)
    for w in all_words:
        all_chars.update(w)
    return (all_words, all_chars)

class G2SDataStream(object):
    def __init__(self, all_instances, word_vocab_enc=None, word_vocab_dec=None, char_vocab=None, edgelabel_vocab=None, options=None,
                 isShuffle=False, isLoop=False, isSort=True, batch_size=-1):
        self.options = options
        if batch_size ==-1: batch_size=options.batch_size
        # index tokens and filter the dataset
        instances = []
        linamr_cover = 0.0
        linamr_total = 0.0
        src_cover = 0.0
        src_total = 0.0
        for (linamr, source, sentence, id) in all_instances:
            if options.max_linamr_len < len(linamr):
                linamr = linamr[:options.max_linamr_len]
            if options.max_src_len < len(source):
                source = source[:options.max_src_len]

            linamr_idx = word_vocab_enc.to_index_sequence_for_list(linamr)
            source_idx = word_vocab_enc.to_index_sequence_for_list(source)
            sentence_idx = word_vocab_dec.to_index_sequence_for_list(sentence[:options.max_answer_len])
            instances.append((linamr_idx, source_idx, sentence_idx, sentence, id))
            linamr_cover += sum(x != word_vocab_enc.vocab_size for x in linamr_idx)
            linamr_total += len(linamr_idx)
            src_cover += sum(x != word_vocab_enc.vocab_size for x in source_idx)
            src_total += len(source_idx)
        print('linamr coverage rate: {}'.format(linamr_cover/linamr_total))
        print('source coverage rate: {}'.format(src_cover/src_total))

        all_instances = instances
        instances = None

        # sort instances based on length
        if isSort:
            all_instances = sorted(all_instances, key=lambda inst: (len(inst[0]), len(inst[1])))
        else:
            random.shuffle(all_instances)
            random.shuffle(all_instances)
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
        self.options = options

        self.instances = instances # list of tuples
        self.batch_size = len(instances)
        self.vocab = word_vocab

        # create length
        self.linamr_len = [] # [batch_size]
        self.src_len = [] # [batch_size]
        self.sent_len = [] # [batch_size]
        for (linamr_idx, source_idx, sentence_idx, sentence, id) in instances:
            self.linamr_len.append(len(linamr_idx))
            self.src_len.append(len(source_idx))
            self.sent_len.append(len(sentence_idx)+1 if len(sentence_idx) < options.max_answer_len else len(sentence_idx))
        self.linamr_len = np.array(self.linamr_len, dtype=np.int32)
        self.src_len = np.array(self.src_len, dtype=np.int32)
        self.sent_len = np.array(self.sent_len, dtype=np.int32)

        # create word representation
        start_id = word_vocab.getIndex('<s>')
        end_id = word_vocab.getIndex('</s>')

        self.linamr = []
        self.src = []
        self.sent_inp = []
        self.sent_out = []
        for (linamr_idx, source_idx, sentence_idx, sentence, id) in instances:
            self.linamr.append(linamr_idx)
            self.src.append(source_idx)
            if len(sentence_idx) < options.max_answer_len:
                self.sent_inp.append([start_id,]+sentence_idx)
                self.sent_out.append(sentence_idx+[end_id,])
            else:
                self.sent_inp.append([start_id,]+sentence_idx[:-1])
                self.sent_out.append(sentence_idx)

        # making ndarray
        self.linamr = padding_utils.pad_2d_vals(self.linamr, len(self.linamr), options.max_linamr_len)
        self.src = padding_utils.pad_2d_vals(self.src, len(self.src), options.max_src_len)
        self.sent_inp = padding_utils.pad_2d_vals(self.sent_inp, len(self.sent_inp), options.max_answer_len)
        self.sent_out = padding_utils.pad_2d_vals(self.sent_out, len(self.sent_out), options.max_answer_len)


if __name__ == "__main__":
    print('all')
    all_instances, _, _, _ = read_amr_file('../data/all.tok_le50.json')
    print('DONE!')

