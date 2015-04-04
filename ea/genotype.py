from abc import ABCMeta, abstractmethod
import numpy as np
import sys, random, math
from config.configuration import Configuration

class GenotypeFactory:
    DEFAULT = "default"

    @staticmethod
    def make_fitness_genotype(genotype=DEFAULT):
        '''
        Factory method create object by the supplied string argument, genotype.
        Configurations are also retrieved and supplied as a kwarg argument for the object.
        '''
        selected = Configuration.get()["genotype"][genotype]
        config = selected["parameters"]
        return getattr(sys.modules[__name__], selected["class_name"])(**config)


class AbstractGenotype(metaclass=ABCMeta):
    '''
    All genotype's  must inherit from AbstractGenotype and implement all it's abstract methods.
    The subclass also has to be registered in the config.json file to work. A genotype must define
    how it's copied, how crossover and mutation works.
    '''

    def __init__(self, crossover_rate=1.0, mutation_rate=0.01):
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate
        self.genotype = None

    @abstractmethod
    def init_random_genotype(self, n):
        pass

    @abstractmethod
    def copy(self):
        pass

    def crossover(self, partner):
        '''
        Default 1 point crossover. Can be overridden by subclasses. If a random number is below the
        crossover_rate a random crossoverpoint is picked. The genotype and partner genotype is then merged
        a new genotype.
        '''
        cg1 = self.copy()
        if random.random() < self.crossover_rate:
            crossover = math.floor(random.uniform(0, self.genotype.size))
            cg1.genotype[:crossover] = partner.genotype[:crossover]
        return cg1

    @abstractmethod
    def mutation(self):
        pass

    def __repr__(self):
        return "G:" + str(self.genotype)


class BitVectorGenotype(AbstractGenotype):
    '''
     #Default genotype, consisting of bits. The bitVectorGenotype define functions for
     copying, initialization, mutation and crossover of itself.
    '''

    def init_random_genotype(self, n):
        '''
        Initially the genotype can be set to a random bit vector.
        '''
        self.genotype = np.random.randint(2, size=n)

    def copy(self):
        '''
        Copy operation for the genotype. Used when children are created with the parents genotype's.
        '''
        g = BitVectorGenotype(crossover_rate=self.crossover_rate, mutation_rate=self.mutation_rate)
        g.genotype = np.empty_like (self.genotype)
        np.copyto(g.genotype, self.genotype)
        return g

    def mutation(self):
        '''
        Single bit mutation. Mutation is considered once. And if mutation is to happen, only one bit is
        flipped.
        '''
        nr_of_chances = 5
        #TODO: consider let number of mutation be a random amount but not all. between 1 - 5 or something.
        for i in range(nr_of_chances):
            if random.random() < self.mutation_rate:
                mutation_point = math.floor(random.uniform(0, self.genotype.size))
                self.genotype[mutation_point] = not self.genotype[mutation_point]
