import numpy as np
class RecurrentNeuralNet:
    '''
    '''
    BIAS_RANGE = [-10.0, 0.0]
    GAIN_RANGE = [1.0, 5.0]
    TIME_RANGE = [1.0, 2.0]
    WEIGHT_RANGE = [-5.0, 5.0]
    SPECIAL_RANGE = [-10.0, 10.0]

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
        nr_recurrent = 2
        sizes = np.array(sizes)
        #TODO: recurrent for 3 output neurons
        incoming_connections = sizes[:-1] + sizes[1:] + nr_bias
        #incoming_connections = sizes[:-1] + nr_recurrent + nr_bias
        neurons = sizes[1:]
        #For each neuron or array, the last nr_bias+nr_recurrent cells are recurrent and bias
        self.weight_matrix_sizes = list(zip(neurons, incoming_connections))


    def _create_internal(self, sizes):

        self.y = [np.zeros(s) for s in sizes[1:]]
        self.prev_output = [np.zeros(s) for s in sizes[1:]]


    def set_weights(self, parameters):
        self.weights = parameters["w"]
        self.gain = parameters["g"]
        self.timeconstants = parameters["t"]

    def restructure_parameters(self, parameters):


        weights = []
        gains = []
        timeconstants = []
        i = 0
        n = 0
        for j, shape in enumerate(self.weight_matrix_sizes):
            n = i + (shape[0] * shape[1])
            #TODO: add gains and weights to create neuron component in genome
            w = np.reshape(self.scaler(parameters[i:n],*self.weight_range),shape)
            w[:,-1] = np.interp( w[:,-1], self.weight_range,self.bias_range)
            if not self.wrap and j == 0:
                w[:, -5] = np.interp(w[:, -5],self.weight_range, self.special_range)
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
        return {"w":weights, "g": gains, "t": timeconstants}


    def input(self, o):
        '''
         The input method propagate the activation from input to output. and returns the activation of the
         output layer
        The dot product of the weights at layer i and the activation from i-1 will result in the activations out from
        neurons at layer i.
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
        self._create_internal(self.sizes)


    @staticmethod
    def scale_number(n, min, max):
        return np.interp(n,[0,1],[min,max])







class CTRNNFactory:

    def __init__(self):
        pass