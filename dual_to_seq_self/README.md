# neural-graph-to-seq
neural graph to sequence model

code structuer:
G2S_trainer.py is the main file for training, it asks G2S_model_graph.py to compile model, and G2S_data_stream.py to prepare data.
G2S_model_graph.py has code for model compiling and executing.
G2S_data_stream.py is for data handling, the original data in json file is in string format, this file does digitalization.
graph_encoder_utils.py contains the graph state LSTM model (our contribution).
encoder_utils.py contains classic sequential encoder code
generator_utils.py contains a decoder code.


