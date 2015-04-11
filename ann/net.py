import numpy as np
import sys
class RecurrentNeuralNet:
    #TODO: Make recurrent network. links in loops, and integrate and fire, more advanced self.activation.
    '''
    Simple feed forward neural network. Does not support backpropagation, so weights have to be adjusted using
    evolution. The init select what type of activation function. tanh and sigmoid supported. threshold and weights matrices
    are also created.

    '''
    BIAS_RANGE = [-10.0, 0.0]
    GAIN_RANGE = [1.0, 5.0]
    TIME_RANGE = [1.0, 2.0]
    WEIGHT_RANGE = [-5.0, 5.0]

    SIGMOID = "sigmoid"
    BIAS_VALUE = 1
    def __init__(self, sizes, weight=WEIGHT_RANGE, bias=BIAS_RANGE, gain=GAIN_RANGE, time=TIME_RANGE):
        self.bias_range = bias
        self.weight_range = weight
        self.gain_range = gain
        self.timeconstant_range = time

        self.num_layers = len(sizes)
        self.sizes = sizes
        self.prev_output = [np.zeros(s) for s in sizes[1:]] #Contain all layers
        self.timeconstants = []
        self.gain = []
        self.mapper = self.create_mapper(sizes)
        self.activation = np.vectorize(RecurrentNeuralNet.sigmoid)

        #TODO:hard coded appending of sizes
        self.weight_matrix_sizes = [(2,8), (2,5)]


    def set_weights(self, parameters):
        #TODO:Reshape etc, structure generator
        self.weights = parameters["w"]
        self.gain = parameters["g"]
        self.timeconstants = parameters["t"]

    def restructure_parameters(self, parameters):
        nr_w = 29
        scaler = np.vectorize(RecurrentNeuralNet.scale_number)
        structured = {}
        weights = []
        i = 0
        n = 0
        for shape in self.weight_matrix_sizes:
            n = i + (shape[0] * shape[1])
            w = scaler(parameters[i:n],*self.weight_range)
            w[-1] = RecurrentNeuralNet.scale_number(parameters[n-1], *self.bias_range)
            weights.append(np.reshape(w, shape))
            i = n
        structured["w"] = weights
        n = i + 4
        structured["g"] = np.reshape(scaler(parameters[i:n], *self.gain_range), (2,2))
        i= n
        n = i+ 4
        structured["t"] = np.reshape(scaler(parameters[i:n], *self.timeconstant_range), (2,2))
        i = n

        return structured

    def create_mapper(self, sizes):
        #TODO: Hardcoded mapper
        mapper = [ [{1: [1,2], 2: [2,1]}], [{1: [1,2], 2: [2,1]}] ]
        #Node one has connection from itself, and 2 in same layer.
        #Could extend to connections between layers
        return mapper

    def input(self, a):
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

        for i, w in enumerate(self.weights):
            a = self._add_recurrent_and_bias(a, i)
            a = self.activation(np.dot(w, a), self.gain[i])
            self.prev_output[i] = a #Prev output kept
        self.a = a
        #sys.exit()

    def output(self):
        return self.a

    def _add_recurrent_and_bias(self, a, i):
        n1 = self.prev_output[i][0]
        n2 = self.prev_output[i][1]
        return np.append(a, [n1,n2,RecurrentNeuralNet.BIAS_VALUE]) #Bias


    @staticmethod
    def scale_number(n, min, max):
        return np.interp(n,[0,1],[min,max])

    @staticmethod
    def sigmoid(y,g):
        return 1.0/(1.0+np.exp(-y*g))





class CTRNNFactory:

    def __init__(self):
        pass