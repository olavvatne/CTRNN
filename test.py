from ea.ea import EA
from tkinter import *
from config.configuration import  Configuration
from gui.visualization import ResultDialog
import numpy as np
from simulator.environment import Environment
import cProfile

class Listner:
    def update(self, c, p, cf, bf, std):
            pass

def show_result(best):
    root = Tk()
    f = Frame(master=root)
    config = Configuration.get()
    result_dialog = ResultDialog(f, best)
    root.mainloop()

def debug_ann(best):
    ann = best.phenotype_container.get_ANN()
    ann.reset()
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

        ann.input(numbers, debug=True)
        m = ann.output()
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


genome_length = 340
pop_size = 20
gen = 40
threshold = 2
ea_system = EA()
listner = Listner()
ea_system.add_listener(listner)
translator = "parameter"
fitness = "tracker"
genotype = "default"
adult = "mixing"
parent = "sigma"

ea_system.setup(translator,fitness,genotype,adult,parent,genome_length)

best = ea_system.run(pop_size, gen, threshold)
debug_ann(best)
show_result(best)



#cProfile.run('ea_system.run(pop_size, gen, threshold)', sort='cumtime')