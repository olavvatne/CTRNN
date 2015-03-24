from ea.ea import EA
import cProfile

class Listner:
    def update(self, c, p, cf, bf, std):
            pass

genome_length = 432
pop_size = 10
gen = 40
threshold = 20
ea_system = EA()
listner = Listner()
ea_system.add_listener(listner)
translator = "weights"
fitness = "flatlands"
genotype = "default"
adult = "full"
parent = "sigma"

ea_system.setup(translator,fitness,genotype,adult,parent,genome_length)


cProfile.run('ea_system.run(pop_size, gen, threshold)', sort='cumtime')
#ea_system.run(pop_size, gen, threshold)
