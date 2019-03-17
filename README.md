# semantic-nmt

This repository contains the codes and the links to the data for our recent paper "[Semantic Neural Machine Translation using AMR](https://arxiv.org/abs/1902.07282)".
In particular, folders "dual_to_seq", "dual_to_seq_dep", "dual_to_seq_self", "dual_to_seq_srl", "dual_to_seq_linamr" and "seq_to_seq" correspond to our models of "Dual2seq", "Dual2seq-Dep", "Dual2seq (self)", "Dual2seq-SRL", "Dual2seq-LinAMR" and "Seq2seq", respectively. 

The codes for "Dual2seq", "Dual2seq-Dep", "Dual2seq (self)" and "Dual2seq-SRL" are mostly identical except the files named "G2S_data_stream.py", which performs data loading and organizing.

## Data

We release our [full WMT16](https://www.cs.rochester.edu/~lsong10/downloads/full_wmt16.tgz) training data and its [NC-v11](https://www.cs.rochester.edu/~lsong10/downloads/nc-v11.tgz) subset with corresponding AMRs, dependency trees and semantic roles. We also release our BPE segmented results and the BPE code file for segmenting other future data.
The dev and test sets are [here]().
