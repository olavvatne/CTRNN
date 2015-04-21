import numpy as np
class RecurrentNeuralNet:
    '''
    '''
    BIAS_RANGE = [-10.0, 0.0]
    GAIN_RANGE = [1.0, 5.0]
    TIME_RANGE = [1.0, 2.0]
    WEIGHT_RANGE = [-5.0, 5.0]
    SPECIAL_RANGE = [-10, 10]

    SIGMOID = "sigmoid"
    BIAS_VALUE = [1]
    def __init__(self, sizes, weight=WEIGHT_RANGE, bias=BIAS_RANGE, gain=GAIN_RANGE, time=TIME_RANGE, wrap=True):
        self.bias_range = bias
        self.wrap = wrap
        self.special_range = RecurrentNeuralNet.SPECIAL_RANGE
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
        sizes = np.array(sizes)
        #TODO: recurrent for 3 output neurons
        #Number of incoming connections for each layer
        incoming_connections = sizes[:-1] + sizes[1:] + nr_bias
        neurons = sizes[1:]
        #For each neuron or array, the last nr_bias+nr_recurrent cells are recurrent and bias
        self.weight_matrix_sizes = list(zip(neurons, incoming_connections))


    def _create_internal(self, sizes):
        '''
        Sets internal properties of neurons to zero. For example
        the previous output that are feed back as activations, or
        the internal state of neurons.
        '''
        self.y = [np.zeros(s) for s in sizes[1:]]
        self.prev_output = [np.zeros(s) for s in sizes[1:]]


    def set_weights(self, parameters):
        self.weights = parameters["w"]
        self.gain = parameters["g"]
        self.timeconstants = parameters["t"]

    def restructure_parameters(self, parameters):
        '''
        A vector evolved from an EA must be restructured to fit
        the CTRNN. Some of the paramaters will be gains, others
        timeconstants and most of them weights. The variable
        weight_matrix_sized and sizes are used to reshape
        the vector into a weight, gain and timeconstant list of vectors or matrices
        '''
        weights = []
        gains = []
        timeconstants = []
        i = 0
        n = 0
        for j, shape in enumerate(self.weight_matrix_sizes):
            n = i + (shape[0] * shape[1])
            #Weights. Last in list a bias weight and have other range
            #TODO: add gains and weights to create neuron component in genome
            w = np.reshape(self.scaler(parameters[i:n],*self.weight_range),shape)
            w[:,-1] = np.interp( w[:,-1], self.weight_range,self.bias_range)

            if not self.wrap and j == 0:
                #For agents with edge detectors. Weight have bigger range than normal weights.
                w[:, 0] = np.interp(w[:, 0],self.weight_range, self.special_range)
                w[:, -4] = np.interp(w[:, -4],self.weight_range, self.special_range)

            weights.append(w)
            i = n

            #Gains
            n = i + self.sizes[j+1]
            gains.append(self.scaler(parameters[i:n], *self.gain_range))
            i= n

            #Timeconstants
            n = i+self.sizes[j+1]
            #Pre divide 1/t. Takes up time in a method run many times
            timeconstants.append(1 / self.scaler(parameters[i:n], *self.timeconstant_range))
            i = n
        #print("w",weights)
        #print("g",gains)
        #print("t",timeconstants)
        return {"w":weights, "g": gains, "t": timeconstants}


    def input(self, o):
        '''
         The input method propagate the activation from input to output. and returns the activation of the
         output layer
        The input method implement the 3 equations neccessary for the
        neurons in CTRNN. Each neuron have a gain and a timeconstant and an
        internal state y.
        In addition to integrating the input*weights from previous layer,
        additional interlayer activations are counted. A weight for bias * 1
        also included. the s variable is the integrated value, used in combination
        with the internal state to calculate a new dy. y is updated using dy, and
        sigmoid of y and gain result in the output of the node.

        Since numpy is used, a whole layer is processed for each iteration using
        operations on vector and matrices, like np.dot, and np.exp
        '''

        y = self.y
        prev_o = self.prev_output
        t_div = self.timeconstants
        g = self.gain
        for i, w in enumerate(self.weights):
            #Equation 1

            #Add recurrent connections and bias
            o = np.concatenate((o, prev_o[i], RecurrentNeuralNet.BIAS_VALUE))
            s = np.dot(w, o)


            #Equation 2 (t_div = 1/t
            #Derivative
            dy = t_div[i] * (-y[i] + s)

            #Equation 3
            y[i] = y[i] + dy

            o = 1.0/(1.0+np.exp(-g[i] * y[i]))
            prev_o[i] = o #Prev output kept
        return o


    def reset(self):
        '''
        Resets internal state of each neuron. Should be called
        before a new environment simulation.
        '''
        self._create_internal(self.sizes)


    @staticmethod
    def scale_number(n, min, max):
        '''
        Scale a number n within range 0, 1 to a new range
        defined by min and max arguments.
        '''
        return np.interp(n,[0,1],[min,max])







class CTRNNFactory:

    def __init__(self):
        pass