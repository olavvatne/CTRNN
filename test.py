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

def show_result(best, ann):
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
    print("W", ann.weights)
    print("G", ann.gain)
    print("T", ann.timeconstants)
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

        print("y", ann.y)
        print("p", ann.prev_output)
        print("m", m)
        diff = m[0] - m[1]
        print("d",diff)
        if diff< 0:
            dir = "Right"
        else:
            dir = "Left"
        v = abs(diff)
        if v <0.2:
            print("Still")
        elif v <0.4:
            print(dir,"1")
        elif v < 0.6:
             print(dir,"2")
        elif v < 0.8:
             print(dir,"3")
        else:
             print(dir,"4")


genome_length = 306
#272 (no pull and wrap)
#352 (pull and wrap)
#296 (no pull and no wrap)

#306 (no pull and wrap) 9 bit
#396 (pull and wrap) 9 bit
#342 (no pull and no wrap) 9 bit
#486 (no wrap no pull) 3 hidden
pop_size = 50
gen = 10
threshold = 30
config = Configuration.get()
ea_system = EA(config)
listner = Listner()
ea_system.add_listener(listner)
translator = "parameter"
fitness = "tracker"
genotype = "default"
adult = "mixing"
parent = "sigma"
ea_system.setup(translator,fitness,genotype,adult,parent,genome_length)

best = ea_system.run(pop_size, gen, threshold)
ann = RecurrentNeuralNet([5,2,2])
p = best.phenotype_container
p = ann.restructure_parameters(p)
ann.set_weights(p)
#ann.weights = [np.array([[-4.45205479,  4.7260274 ,  4.08023483,  1.9667319 , -3.63013699,
#        -0.85127202, -0.26418787, -3.48336595],
#       [ 1.55577299,  2.47553816,  4.88258317, -2.20156556, -3.53228963,
#        -2.16242661, -3.59099804, -5.14677104]]), np.array([[ 3.66927593,  1.51663405,  1.36007828,  1.63405088, -4.52054795],
#       [-2.12328767, -1.30136986,  4.29549902, -0.02935421, -0.01956947]])]
#ann.gain = [np.array([ 2.31506849,  1.56360078]), np.array([ 2.95694716,  3.81017613])]
#ann.timeconstants = [np.array([ 0.90123457,  0.67503303]), np.array([ 0.82154341,  0.80472441])]
debug_ann(ann)
show_result(best, ann)


#cProfile.run('speed_ann(ann)', sort='cumtime')
#cProfile.run('time_test()', sort='cumtime')
cProfile.run('ea_system.run(pop_size, gen, threshold)', sort='cumtime')