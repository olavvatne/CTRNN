from tkinter import Toplevel, Button
from simulator.environment import Environment

class ResultDialog(object):
    '''

    '''
    def __init__(self, parent, individual, config):
        self.config = config
        #TODO: Generate a new scenario. But what to do for static?
        self.scenario = self.create_environment()
        top = self.top = Toplevel(parent)
        top.title("Flatlands - results")

        b = Button(top, text="OK", command=self.ok)
        b.pack(pady=5)

    def create_environment(self):
        dim = self.config["fitness"]["flatlands"]["grid_dimension"]
        return Environment(dim)
    
    def ok(self):
        self.update()
        self.top.destroy()