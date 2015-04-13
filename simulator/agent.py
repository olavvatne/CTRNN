from ann.net import RecurrentNeuralNet
from simulator.environment import Environment
import numpy as np
class Simulator():

    def __init__(self):
        self.layers = [5,2,2]
        self.agent = RecurrentNeuralNet(self.layers)
        self.environment = Environment(30,15)

    def run(self, p, rec=False):
         parameters = self.agent.restructure_parameters(np.array(p))
         self.agent.set_weights(parameters)
         return self.environment.score_agent(self.agent, timesteps=600, rec= rec)

    def get_recording(self):
        return self.environment.get_recording()