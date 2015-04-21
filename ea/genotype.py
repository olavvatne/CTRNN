from abc import ABCMeta, abstractmethod
import numpy as np
import sys, random, math
from config.configuration import Configuration
from ea.translator import BinToParameterTranslator

class GenotypeFactory:
    DEFAULT = "default"

    @staticmethod
    def make_genotype(genotype=DEFAULT, config=None):
        '''
        Factory method create object by the supplied string argument, genotype.
        Configurations are also retrieved and supplied as a kwarg argument for the object.
        '''
        if not config:
            selected = Configuration.get()["genotype"][genotype]
        else:
            selected = config["genotype"][genotype]
        config = selected["parameters"]
        return getattr(sys.modules[__name__], selected["class_name"])(**config)


class AbstractGenotype(metaclass=ABCMeta):
    '''
    All genotype's  must inherit from AbstractGenotype and implement all it's abstract methods.
    The subclass also has to be registered in the config.json file to work. A genotype must define
    how it's copied, how crossover and mutation works.
    '''

    def __init__(self, crossover_rate=1.0, mutation_rate=0.01):
        #print("cross_over: ", crossover_rate, " , mutation_rate :", mutation_rate)
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate
        self.genotype = None
        #TODO: parameterize
        self.k = Configuration.get()["translator"]["parameter"]["parameters"]["k"]

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
        # t = n/self.k
        #mu = (2**self.k)/2
        #sigma = math.sqrt(mu)*8
        #print(sigma)
        #numbers = np.random.normal(mu, sigma, t)
        #genotype = []
        #print("lol")
        #for i in numbers:
        #    print(i)
        #    binary = self._int2bin(int(max(min(i, 2**self.k), 0)))
        #    padding = [0 for v in range(self.k - len(binary))]
        #    genotype.extend(self._bin2gray(padding + binary))
        #self.genotype = np.array(genotype)
        self.genotype = np.random.randint(2, size=n)

    def _bin2gray(self, bits):
	    return bits[:1] + [i ^ ishift for i, ishift in zip(bits[:-1], bits[1:])]

    def _int2bin(n):
        'From positive integer to list of binary bits, msb at index 0'
        if n:
            bits = []
            while n:
                n,remainder = divmod(n, 2)
                bits.insert(0, remainder)
            return bits
        else: return [0]

    def crossover(self, partner):
        '''
        Crossover with a twist. Will crossover only in between weights
        '''
        cg1 = self.copy()
        if random.random() < self.crossover_rate:
            #crossover = crossover - (crossover%self.k)
            #crossover = math.floor(random.uniform(0, self.genotype.size))
            for i in range(0, self.genotype.size, self.k):
                if i%(self.k*2):
                    cg1.genotype[i:i+self.k] = partner.genotype[i:i+self.k]

        return cg1

    def copy(self):
        '''
        Copy operation for the genotype. Used when children are created with the parents genotype's.
        '''
        g = BitVectorGenotype(crossover_rate=self.crossover_rate, mutation_rate=self.mutation_rate)
        g.genotype = np.copy(self.genotype)
        np.copyto(g.genotype, self.genotype)
        return g

    def mutation(self):
        '''
        Single bit mutation. Mutation is considered once. And if mutation is to happen, only one bit is
        flipped.
        '''
        nr_of_chances = 1
        for i in range(nr_of_chances):
            if random.random() < self.mutation_rate:
                mutation_point = math.floor(random.uniform(0, self.genotype.size))
                self.genotype[mutation_point] = not self.genotype[mutation_point]
