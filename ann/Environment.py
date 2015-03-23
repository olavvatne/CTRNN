import numpy as np


class Environment:

    def __init__(self, dim, f_prob=0.333, p_prob=0.333):
        #F_prob of a cell being filled with food, and p_prob that a remaining empty cell
        #is filled with poisoon
        probabilites = [1-f_prob-(f_prob*(1-p_prob)), f_prob, f_prob*(1-p_prob)]
        self.board = np.random.choice(3, replace=True, p=probabilites, size=(dim, dim))

    def score_agent(self, agent, timesteps=60):
        b = None
        np.copyto(b, self.board)
        #TODO: Might consider using a structure to keep track of changes made
        #to board while sim
        food = 0
        poison = 0
        for i in range(timesteps):
            #Move the agent about using ann of agent
            #Send sensor data and get motor data out and see what happens.
            #TODO: Make agent and ann
            pass
        return (food, poison)


    def __repr__(self):
        return str(self.board)

