import numpy as np

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
    BIAS = 1
    def __init__(self, sizes, weight=WEIGHT_RANGE, bias=BIAS_RANGE, gain=GAIN_RANGE, time=TIME_RANGE):
        self.bias_range = bias
        self.weight_range = weight
        self.gain_range = gain
        self.timeconstant_range = time

        self.num_layers = len(sizes)
        self.sizes = sizes
        self.prev_output = [np.zeros(s) for s in sizes] #Contain all layers
        self.timeconstants = []
        self.gain = []
        self.mapper = self.create_mapper(sizes)
        self.activation = np.vectorize(RecurrentNeuralNet.sigmoid)


        #Threshold is set to output a constant 1. Threshold for every neuron in all layers except input layer.
        self.weight_matrix_sizes = zip(sizes[:-1], sizes[1:])
        self.weights = [np.random.randn(y, x) for x, y in self.weight_matrix_sizes]

    def set_weights(self, parameters):
        #TODO:Reshape etc, structure generator
        self.weights = parameters

    def restructure_parameters(self, parameters):
        #weight_structure = [np.empty([y, x]) for x, y in  self.weight_sizes]
        #phenotype = self._transfer(weight_numbers, weight_structure)
        pass

    def _transfer(self, phenotype, weight_structure):
        '''
        Transfer transform the weights from a linear list to match the layer structure of the ANN. The resulting
        weight structure can then replace the existing weights in the ANN.
        '''
        n = 0
        for w in weight_structure:
            for i in range(len(w)):
                for j in range(len(w[i])):
                    w[i][j] = phenotype[n]
                    n += 1
        return weight_structure

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
        g = 0
        for w in self.weights:

            np.append(a, RecurrentNeuralNet.BIAS) #Bias
            a = self.activation(np.dot(w, a), g)
        self.a = a

    def output(self):
        return self.a

    def add_recurrent_and_bias(self, a, i):
        pass

    def sigmoid(y,g):
        return 1.0/(1.0+np.exp(-y*g))





class CTRNNFactory:

    def __init__(self):
        pass