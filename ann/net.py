import numpy as np
import sys
class RecurrentNeuralNet:
    '''
    '''
    BIAS_RANGE = [-10.0, 0.0]
    GAIN_RANGE = [1.0, 5.0]
    TIME_RANGE = [1.0, 2.0]
    WEIGHT_RANGE = [-5.0, 5.0]

    SIGMOID = "sigmoid"
    BIAS_VALUE = [1]
    def __init__(self, sizes, weight=WEIGHT_RANGE, bias=BIAS_RANGE, gain=GAIN_RANGE, time=TIME_RANGE):
        self.bias_range = bias
        self.weight_range = weight
        self.gain_range = gain
        self.timeconstant_range = time
        self.scaler = np.vectorize(RecurrentNeuralNet.scale_number)
        self.sizes = sizes
        self.timeconstants = []
        self.gain = []
        self._create_internal(sizes)

        #Assume same number  of recurrent and bias connection for all hidden and output
        nr_bias = 1
        nr_recurrent = 2
        sizes = np.array(sizes)
        incoming_connections = sizes[:-1] + nr_recurrent + nr_bias
        neurons = sizes[1:]
        #For each neuron or array, the last nr_bias+nr_recurrent cells are recurrent and bias
        self.weight_matrix_sizes = list(zip(neurons, incoming_connections))


    def _create_internal(self, sizes):

        self.y = [np.zeros(s) for s in sizes]
        self.prev_output = [np.zeros(s) for s in sizes]


    def set_weights(self, parameters):
        self.weights = parameters["w"]
        self.gain = parameters["g"]
        self.timeconstants = parameters["t"]

    def restructure_parameters(self, parameters):


        weights = []
        gains = [[]]
        timeconstants = [[]]
        i = 0
        n = 0
        for j, shape in enumerate(self.weight_matrix_sizes):
            n = i + (shape[0] * shape[1])
            #TODO: add gains and weights to create neuron component in genome
            w = self.scaler(parameters[i:n],*self.weight_range)
            w[-1] = RecurrentNeuralNet.scale_number(parameters[n-1], *self.bias_range)
            weights.append(np.reshape(w, shape))
            i = n

            #Gains
            n = i + self.sizes[j+1]
            gains.append(self.scaler(parameters[i:n], *self.gain_range))
            i= n

            #Timeconstants
            n = i+self.sizes[j+1]
            timeconstants.append(self.scaler(parameters[i:n], *self.timeconstant_range))
            i = n

        return {"w":weights, "g": gains, "t": timeconstants}

    #def create_mapper(self, sizes):
    #    #TODO: Hardcoded mapper, not even used currently
    #    mapper = [ [{1: [1,2], 2: [2,1]}], [{1: [1,2], 2: [2,1]}] ]
    #    #Node one has connection from itself, and 2 in same layer.
    #    #Could extend to connections between layers
    #   return mapper

    def input(self, external_input):

        '''
         The input method propagate the activation from input to output. and returns the activation of the
         output layer
        The dot product of the weights at layer i and the activation from i-1 will result in the activations out from
        neurons at layer i.
        '''
        #debug=True

        #If input layer should be treated as same type of nodes.
        #s = external_input #Only external input, no weights and such. Does still have internal y
        #dy = self.derivative(self.y[0], s, self.timeconstants[0])
        #self.y[0] = self.y[0] + dy
        #o = self.sigmoid(self.y[0], self.gain[0])

        o = external_input

        for j, w in enumerate(self.weights):
            #Equation 1

            #Add recurrent connections and bias
            o = np.concatenate((o, self.prev_output[j+1], RecurrentNeuralNet.BIAS_VALUE))

            s = np.dot(w, o)


            #Equation 2
            #Derivative
            dy = np.multiply(1/self.timeconstants[j+1],((-self.y[j+1])+s))

            #Equation 3
            self.y[j+1] = self.y[j+1] + dy

            o = self.sigmoid(self.y[j+1], self.gain[j+1])

            self.prev_output[j+1] = o #Prev output kept
        return o

    def sigmoid(self, y,g):
        return 1.0/(1.0+np.exp(np.multiply(-y,g)))

    def derivative(self, y, s, t):
        return np.multiply(1/t,((-y)+s))

    def reset(self):
        self._create_internal(self.sizes)

    @staticmethod
    def scale_number(n, min, max):
        return np.interp(n,[0,1],[min,max])







class CTRNNFactory:

    def __init__(self):
        pass