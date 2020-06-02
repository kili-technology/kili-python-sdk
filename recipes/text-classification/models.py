import tensorflow as tf


class bi_LSTM(tf.keras.Model):

    def __init__(self, input_review_size=300, vocabulary_size=20000, n_word_embedding=50, n_hidden=50):
        super(bi_LSTM, self).__init__()
        self.embedding = tf.keras.layers.Embedding(
            input_dim=vocabulary_size,
            output_dim=n_word_embedding,
            input_length=input_review_size)
        self.max_pooling = tf.keras.layers.GlobalMaxPooling1D()
        self.lstm = tf.keras.layers.LSTM(
            n_hidden,
            recurrent_dropout=0.5,
            recurrent_activation=tf.nn.relu)
        self.bidirectional_lstm = tf.keras.layers.Bidirectional(self.lstm)
        self.dense = tf.keras.layers.Dense(50, activation=tf.nn.relu)
        self.out = tf.keras.layers.Dense(1, activation=tf.nn.softmax)

    def call(self, inputs, training=False):
        x = self.embedding(inputs)
        x = self.max_pooling(x)
        x = self.bidirectional_lstm(x)
        x = self.dense(x)
        return(self.out(x))
