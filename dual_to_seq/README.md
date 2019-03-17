# Dual2seq

The Dual2seq model takes two sources as input: the source sentence and a corresponding AMR graph.
A GRN-based encoder and a sequential encoder encodes both inputs.
The doubly-attentive LSTM decoder pays attentions both on the graph nodes and on the source sentence.
More information is in our [paper](https://arxiv.org/abs/1902.07282)
