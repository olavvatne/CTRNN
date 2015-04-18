from ea.ea import EA
from tkinter import *
from config.configuration import  Configuration
from gui.visualization import ResultDialog
from ann.net import RecurrentNeuralNet
import numpy as np
import cProfile
import sys

class Listner:
    def update(self, c, p, cf, bf, std):
            pass

def show_result(best):
    root = Tk()
    f = Frame(master=root)
    config = Configuration.get()
    result_dialog = ResultDialog(f, best)
    root.mainloop()

def speed_ann(ann):
    for i in range(70*10*600):
        numbers = np.empty(5)
        m = ann.input(numbers)

def time_test():
    o = np.array([0.55, 0.553, 3.4545, 5.2342, 2.23423])
    y = np.array([.343,.3423])
    s = np.array([0.534, 0.234])
    a = 0
    for i in range(70*10*600):
         for t in y:
             pass

def debug_ann(ann):
    while(True):
        #print("y", ann.y)
        #print("gain",ann.gain)
        #print("timeconstants",ann.timeconstants)
        #print("weights",ann.weights)
        txt = input('Test ANN:')
        if txt == 'q':
            break
        elif txt == 'r':
            ann.reset()
        try:
            numbers = np.array([int(x) for x in txt.split(sep=" ")])
            print(numbers)
        except:
            print("Not valid!")
            continue

        m = ann.input(numbers)
        print(m)
        diff = m[0] - m[1]
        print(diff)
        if diff< 0:
            dir = "Left"
        else:
            dir = "Right"
        v = abs(diff)
        if v <0.1:
            print("Still")
        elif v <0.25:
            print(dir,"1")
        elif v < 0.5:
             print(dir,"2")
        elif v < 0.65:
             print(dir,"3")
        else:
             print(dir,"4")


genome_length = 500
pop_size = 10
gen = 100
threshold = 7
ea_system = EA()
listner = Listner()
ea_system.add_listener(listner)
translator = "parameter"
fitness = "tracker"
genotype = "default"
adult = "full"
parent = "sigma"

ea_system.setup(translator,fitness,genotype,adult,parent,genome_length)

best = ea_system.run(pop_size, gen, threshold)
ann = RecurrentNeuralNet([5,2,2])
p = best.phenotype_container
p = ann.restructure_parameters(p)
ann.set_weights(p)
#debug_ann(ann)
show_result(best)


#cProfile.run('speed_ann(ann)', sort='cumtime')
#cProfile.run('time_test()', sort='cumtime')
#cProfile.run('ea_system.run(pop_size, gen, threshold)', sort='cumtime')