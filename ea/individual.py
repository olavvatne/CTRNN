import numpy as np
class Individual(object):
    '''
    An individual contains a genotype, phenotype, a translator (genotype to phenotype mapper), and fitness value
    This is something all EA problems have in common and are represented in this class.
    All individuals have functions for mating, copying and developing.
    '''

    def __init__(self, genotype, translator):
        self.genotype_container = genotype
        self.translator = translator
        self.phenotype_container = None
        self.fitness = None
        self.adult = False

    def devlop(self):
        '''
        Devlop use the supplied translator's develop method to generate a phenotype from the
        individuals genotype
        '''
        self.phenotype_container = self.translator.develop(self)

    def mate(self, partner):
        '''
        Mating involves crossover and mutation. A mating produce 2 children that are possibly
        a mix of it's parents. The genotype of the individual are crossed with the partner's genome
        and vice versa. The new genotype's are then mutated and two new individual object initalized
        and returned.
        '''
        #print(self, partner)
        g1 = self.genotype_container.crossover(partner.genotype_container)
        g2 = partner.genotype_container.crossover(self.genotype_container)
        g1.mutation()
        g2.mutation()
        return (Individual(g1, self.translator), Individual(g2, self.translator))

    def copy(self):
        return Individual(self.genotype_container, self.translator)

    def __repr__(self):
        return "F: " +str(self.fitness) #+" G:" + str(self.genotype_container)