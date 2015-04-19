from ann.net import RecurrentNeuralNet
from simulator.environment import Environment
import numpy as np
class Simulator():

    def __init__(self, pull=False, wrap=True):
        self.layers = [5,2,2]
        if not wrap:
            self.layers[0] = 7
           # self.layers[1] = 3
        if pull:
            self.layers[2] = 3

        self.agent = RecurrentNeuralNet(self.layers, wrap=wrap)
        self.environment = Environment(30,15, pull=pull, wrap=wrap)

    def run(self, p, rec=False, timesteps=600):
         return self.environment.score_agent(self.agent, timesteps=timesteps, rec= rec)

    def set(self, p):
        parameters = self.agent.restructure_parameters(p)
        self.agent.set_weights(parameters)

    def get_recording(self):
        return self.environment.get_recording()