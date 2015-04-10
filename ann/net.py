import numpy as np

class RecurrentNeuralNet:
    #TODO: Make recurrent network. links in loops, and integrate and fire, more advanced self.activation.
    '''
    Simple feed forward neural network. Does not support backpropagation, so weights have to be adjusted using
    evolution. The init select what type of activation function. tanh and sigmoid supported. threshold and weights matrices
    are also created.

    '''
    SIGMOID = "sigmoid"
    TANH = "tanh"

    def __init__(self, sizes, activation=SIGMOID):
        self.num_layers = len(sizes)
        self.sizes = sizes

        if activation == RecurrentNeuralNet.SIGMOID:
            self.activation = np.vectorize(sigmoid)
        else:
            self.activation = np.vectorize(tanh)

        #Threshold is set to output a constant 1. Threshold for every neuron in all layers except input layer.
        self.thesholds = [np.full(y, 0.7) for y in sizes[1:]]
        weight_matrix_sizes = zip(sizes[:-1], sizes[1:])
        self.weights = [np.random.randn(y, x) for x, y in weight_matrix_sizes]

    def set_weights(self, weights):
        self.weights = weights

    def feedforward(self, a):
        #TODO: how to incorporate activation levels etc.
        #TODO: Need to rething, since activation levels must be kept between
        #timsteps
        #Probably store
        '''
         The feedforward method propagate the activation from input to output. and returns the activation of the
         output layer
        The dot product of the weights at layer i and the activation from i-1 will result in the activations out from
        neurons at layer i.
        '''
        for t, w in zip(self.thesholds, self.weights):
            a = self.activation(np.dot(w, a)+t)
        return a


def sigmoid(z):
    return 1.0/(1.0+np.exp(-z))

def tanh(x):
    return np.tanh(x)

class CTRNNFactory:

    def __init__(self):
        pass