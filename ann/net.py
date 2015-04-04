import numpy as np

class FeedForwardNet:

    SIGMOID = "sigmoid"
    TANH = "tanh"

    def __init__(self, sizes, activation=SIGMOID):
        self.num_layers = len(sizes)
        self.sizes = sizes

        if activation == FeedForwardNet.SIGMOID:
            #print("SIGMOID")
            self.activation = np.vectorize(sigmoid)
        else:
            #print("TANH")
            self.activation = np.vectorize(tanh)
        #self.biases = [np.random.randn(y) for y in sizes[1:]]
        self.biases = [np.ones(y) for y in sizes[1:]]
        weight_matrix_sizes = zip(sizes[:-1], sizes[1:])
        self.weights = [np.random.randn(y, x) for x, y in weight_matrix_sizes]

    def set_weights(self, weights):
        self.weights = weights

    def feedforward(self, a):
        for b, w in zip(self.biases, self.weights):
            a = self.activation(np.dot(w, a)+b)
        return a


def sigmoid(z):
    return 1.0/(1.0+np.exp(-z))

def tanh(x):
    return np.tanh(x)

