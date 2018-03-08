This model takes two sources of input: source AMR graph and source sentence.
A graph encoder and a sequential encoder encodes both inputs, respectively.
The decoder is an attention-based LSTM with attentions both on the graph nodes and on the source sentence.
