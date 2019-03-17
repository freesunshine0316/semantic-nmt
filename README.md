# semantic-nmt

This repository contains the codes and the links to the data for our recent paper "[Semantic Neural Machine Translation using AMR](https://arxiv.org/abs/1902.07282)".
In particular, folders "dual_to_seq", "dual_to_seq_dep", "dual_to_seq_self", "dual_to_seq_srl", "dual_to_seq_linamr" and "seq_to_seq" correspond to our models of "Dual2seq", "Dual2seq-Dep", "Dual2seq (self)", "Dual2seq-SRL", "Dual2seq-LinAMR" and "Seq2seq", respectively. 

The codes for "Dual2seq", "Dual2seq-Dep", "Dual2seq (self)" and "Dual2seq-SRL" are mostly identical except the files named "G2S_data_stream.py", which performs data loading and organizing.

Please create issues if there are any questions! This can make things more tractable.

## Data release

We release our [full WMT16](https://www.cs.rochester.edu/~lsong10/downloads/full_wmt16.tgz) training data and its [NC-v11](https://www.cs.rochester.edu/~lsong10/downloads/nc-v11.tgz) subset with corresponding AMRs, dependency trees and semantic roles. We also release our BPE segmented results and the BPE code file for segmenting other future data.
The dev and test sets are [here](https://www.cs.rochester.edu/~lsong10/downloads/devtest.tgz).

## System training and decoding

Simply go to the corresponding folder and check these "*.sh" scripts. 
The code is developed under TensorFlow 1.4.1 and heavily depends on our previous repository on "[A Graph-to-Sequence Model for AMR-to-Text Generation](https://github.com/freesunshine0316/neural-graph-to-seq-mp)".


## Cite

If you like our paper, please cite
```
@Article{song-tacl19,
  author = {Linfeng Song and Daniel Gildea and Yue Zhang and Zhiguo Wang and
  Jinsong Su},
  title = {Semantic Neural Machine Translation using {AMR}},
  journal = {Transactions of the Association for Computational Linguistics
  (TACL)},
  year = {2019},
  URL = {https://www.cs.rochester.edu/u/gildea/pubs/song-tacl19.pdf}
}
```
