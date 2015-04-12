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
    while(True):
        ann.reset()
        print("y", ann.y)
        print("gain",ann.gain)
        print("timeconstants",ann.timeconstants)
        print("weights",ann.weights)
        txt = input('Test ANN:')
        if txt == 'q':
            break
        try:
            numbers = np.array([int(x) for x in txt.split(sep=" ")])
            print(numbers)
            ann.input(numbers)
            m = ann.output()
            print(m)

        except:
            print("Not valid!")
    pass

genome_length = 440
pop_size = 30
gen = 10
threshold = 1.1
ea_system = EA()
listner = Listner()
ea_system.add_listener(listner)
translator = "parameter"
fitness = "tracker"
genotype = "default"
adult = "full"
parent = "tournament"

ea_system.setup(translator,fitness,genotype,adult,parent,genome_length)

best = ea_system.run(pop_size, gen, threshold)
debug_ann(best)
show_result(best)



#cProfile.run('ea_system.run(pop_size, gen, threshold)', sort='cumtime')