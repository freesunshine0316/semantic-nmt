import tensorflow as tf
import graph_encoder_utils
import encoder_utils
import generator_utils
import padding_utils
from tensorflow.python.ops import variable_scope
import numpy as np
import random


class ModelGraph(object):
    def __init__(self, word_vocab_enc, word_vocab_dec, options=None, mode='ce_train'):
        # here 'mode', whose value can be:
        #  'ce_train',
        #  'rl_train',
        #  'evaluate',
        #  'evaluate_bleu',
        #  'decode'.
        # it is different from 'mode_gen' in generator_utils.py
        # value of 'mode_gen' can be ['ce_loss', 'rl_loss', 'greedy' or 'sample']
        self.mode = mode

        # is_training controls whether to use dropout
        is_training = True if mode in ('ce_train', ) else False

        self.options = options
        self.word_vocab_enc = word_vocab_enc
        self.word_vocab_dec = word_vocab_dec

        self.create_placeholders(options)

        # encode the input instance
        # encoder.graph_hidden [batch, node_num, vsize]
        # encoder.graph_cell [batch, node_num, vsize]
        with tf.variable_scope('linamr_encoder'):
            self.linamr_encoder = encoder_utils.SeqEncoder(options,
                    word_vocab = word_vocab_enc)
            self.linamr_hidden_dim, self.linamr_hiddens, self.linamr_decinit = \
                    self.linamr_encoder.encode(is_training=is_training)
            self.linamr_words = self.linamr_encoder.in_passage_words
            self.linamr_lengths = self.linamr_encoder.passage_lengths
            self.linamr_mask = self.linamr_encoder.passage_mask

        with tf.variable_scope('src_encoder'):
            self.src_encoder = encoder_utils.SeqEncoder(options,
                    word_vocab=word_vocab_enc)
            self.src_hidden_dim, self.src_hiddens, self.src_decinit = \
                    self.src_encoder.encode(is_training=is_training)
            self.src_words = self.src_encoder.in_passage_words
            self.src_lengths = self.src_encoder.passage_lengths
            self.src_mask = self.src_encoder.passage_mask

        # ============== Choices of initializing decoder state =============
        if options.way_init_decoder == 'src':
            new_c, new_h = self.src_decinit.c, self.src_decinit.h
        elif options.way_init_decoder == 'linamr':
            new_c, new_h = self.linamr_decinit.c, self.linamr_decinit.h
        elif options.way_init_decoder == 'zero':
            new_c = tf.zeros([self.encoder.batch_size, options.gen_hidden_size])
            new_h = tf.zeros([self.encoder.batch_size, options.gen_hidden_size])
        else:
            assert False, 'way to initial decoder (%s) not supported' % options.way_init_decoder
        self.init_decoder_state = tf.contrib.rnn.LSTMStateTuple(new_c, new_h)

        # prepare src-side input for decoder

        loss_weights = tf.sequence_mask(self.answer_len, options.max_answer_len, dtype=tf.float32) # [batch_size, gen_steps]

        with variable_scope.variable_scope("generator"):
            # create generator
            self.generator = generator_utils.CovAttenGen(self, options, word_vocab_dec, is_training=is_training)
            # calculate encoder_features
            with variable_scope.variable_scope("encoder_feats"):
                self.linamr_features = self.generator.calculate_encoder_features(
                        self.linamr_hiddens, self.linamr_hidden_dim)

            with variable_scope.variable_scope("src_feats"):
                self.src_features = self.generator.calculate_encoder_features(
                        self.src_hiddens, self.src_hidden_dim)

            if mode == 'decode':
                self.context_encoder_t_1 = tf.placeholder(tf.float32,
                        [None, self.linamr_hidden_dim], name='context_encoder_t_1') # [batch_size, encoder_dim]
                self.context_src_t_1 = tf.placeholder(tf.float32,
                        [None, self.src_hidden_dim], name='context_src_t_1') # [batch_size, src_dim]
                if options.use_coverage:
                    self.coverage_t_1 = tf.placeholder(tf.float32, [None, None], name='coverage_t_1') # [batch_size, encoder_dim]
                else:
                    self.coverage_t_1 = None
                self.word_t = tf.placeholder(tf.int32, [None], name='word_t') # [batch_size]

                (self.state_t, self.context_encoder_t, self.context_src_t,
                        self.coverage_t, self.attn_dist_t, self.ouput_t,
                        self.topk_log_probs, self.topk_ids, self.greedy_prediction, self.multinomial_prediction) = \
                            self.generator.decode_mode(
                        word_vocab_dec, options.beam_size, self.init_decoder_state,
                        self.context_encoder_t_1, self.context_src_t_1, self.coverage_t_1, self.word_t,
                        self.linamr_hiddens, self.linamr_features, self.linamr_mask,
                        self.src_hiddens, self.src_features, self.src_mask)
                # not buiding training op for this mode
                return
            elif mode == 'evaluate_bleu':
                _, _, self.greedy_words = self.generator.train_mode(word_vocab_dec,
                    self.linamr_hidden_dim, self.linamr_hiddens, self.linamr_features, self.linamr_mask,
                    self.src_hidden_dim, self.src_hiddens, self.src_features, self.src_mask,
                    self.init_decoder_state, self.answer_inp, self.answer_ref, loss_weights, mode_gen='greedy')
                # not buiding training op for this mode
                return
            elif mode in ('ce_train', 'evaluate', ):
                self.accu, self.loss, _ = self.generator.train_mode(word_vocab_dec,
                    self.linamr_hidden_dim, self.linamr_hiddens, self.linamr_features, self.linamr_mask,
                    self.src_hidden_dim, self.src_hiddens, self.src_features, self.src_mask,
                    self.init_decoder_state, self.answer_inp, self.answer_ref, loss_weights, mode_gen='ce_loss')
                if mode == 'evaluate': return # not buiding training op for evaluation

        with tf.device('/gpu:1'):
            if options.optimize_type == 'adadelta':
                optimizer = tf.train.AdadeltaOptimizer(learning_rate=options.learning_rate)
            elif options.optimize_type == 'adam':
                optimizer = tf.train.AdamOptimizer(learning_rate=options.learning_rate)
            clipper = 50 if not options.__dict__.has_key("max_gradient_norm") else options.max_gradient_norm
            print("MAX gradient norm {}".format(clipper))
            tvars = tf.trainable_variables()
            if options.lambda_l2>0.0:
                l2_loss = tf.add_n([tf.nn.l2_loss(v) for v in tvars if v.get_shape().ndims > 1])
                self.loss = self.loss + options.lambda_l2 * l2_loss
            grads, _ = tf.clip_by_global_norm(tf.gradients(self.loss, tvars), clipper)
            self.train_op = optimizer.apply_gradients(zip(grads, tvars))

            extra_train_ops = []
            train_ops = [self.train_op] + extra_train_ops
            self.train_op = tf.group(*train_ops)

    def create_placeholders(self, options):
        # build placeholder for answer
        self.answer_ref = tf.placeholder(tf.int32, [None, options.max_answer_len], name="answer_ref") # [batch_size, gen_steps]
        self.answer_inp = tf.placeholder(tf.int32, [None, options.max_answer_len], name="answer_inp") # [batch_size, gen_steps]
        self.answer_len = tf.placeholder(tf.int32, [None], name="answer_len") # [batch_size]


    def run_greedy(self, sess, batch, options):
        feed_dict = self.run_encoder(sess, batch, options, only_feed_dict=True) # reuse this function to construct feed_dict
        feed_dict[self.answer_inp] = batch.sent_inp
        return sess.run(self.greedy_words, feed_dict)


    def run_ce_training(self, sess, batch, options, only_eval=False):
        feed_dict = self.run_encoder(sess, batch, options, only_feed_dict=True) # reuse this function to construct feed_dict
        feed_dict[self.answer_inp] = batch.sent_inp
        feed_dict[self.answer_ref] = batch.sent_out
        feed_dict[self.answer_len] = batch.sent_len

        if only_eval:
            return sess.run([self.accu, self.loss], feed_dict)
        else:
            return sess.run([self.train_op, self.loss], feed_dict)[1]


    def run_encoder(self, sess, batch, options, only_feed_dict=False):
        feed_dict = {}
        feed_dict[self.linamr_lengths] = batch.linamr_len
        feed_dict[self.linamr_words] = batch.linamr
        feed_dict[self.src_lengths] = batch.src_len
        feed_dict[self.src_words] = batch.src

        if only_feed_dict:
            return feed_dict

        return sess.run([self.linamr_hiddens, self.linamr_features, self.linamr_mask,
            self.src_hiddens, self.src_features, self.src_mask, self.init_decoder_state],
                feed_dict)

if __name__ == '__main__':
    summary = " Tokyo is the one of the biggest city in the world."
    reference = "The capital of Japan, Tokyo, is the center of Japanese economy."
    print sentence_rouge(reference, summary)

