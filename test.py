from ea.ea import EA
from tkinter import *
from config.configuration import  Configuration
from gui.visualization import ResultDialog
import cProfile

class Listner:
    def update(self, c, p, cf, bf, std):
            pass


genome_length = 432
pop_size = 20
gen = 100
threshold = 30
ea_system = EA()
listner = Listner()
ea_system.add_listener(listner)
translator = "weights"
fitness = "flatlands"
genotype = "default"
adult = "full"
parent = "sigma"

ea_system.setup(translator,fitness,genotype,adult,parent,genome_length)

best = ea_system.run(pop_size, gen, threshold)
root = Tk()
f = Frame(master=root)
config = Configuration.get()
result_dialog = ResultDialog(f, best, config)
root.mainloop()
#cProfile.run('ea_system.run(pop_size, gen, threshold)', sort='cumtime')
#ea_system.run(pop_size, gen, threshold)
