from abc import ABCMeta, abstractmethod
import sys
import math

import numpy as np

from ea.phenotype import IntegerPhenotype
from config.configuration import Configuration


class TranslatorFactory:
    DEFAULT = "default"

    @staticmethod
    def make_fitness_translator(translator=DEFAULT):
        '''
        Factory method create object by the supplied string argument, translator.
        Configurations are also retrieved and supplied as a kwarg argument for the object.
        '''
        selected = Configuration.get()["translator"][translator]
        config = selected["parameters"]
        print(config)
        return getattr(sys.modules[__name__], selected["class_name"])(**config)


class AbstractTranslator(metaclass=ABCMeta):
    '''
    All adult translators must inherit from AbstractTranslator, implement the develop method and
    be registered in config.json to be acceptable as a adult selection class.
    '''

    def __init__(self, **kwargs):
        pass

    @abstractmethod
    def develop(self, individual):
        pass


class DefaultTranslator(AbstractTranslator):
    '''
    DefaultTranslator use IntegerPhenotype and simply copies the genotype over.
    '''

    def develop(self, individual):
        '''
        Genotype simply copied, and a IntegerPhenotype created
        '''
        return IntegerPhenotype(np.copy(individual.genotype_container.genotype))


class BinToIntTranslator(AbstractTranslator):
    '''
    BinToIntTranslator takes a bit vector and create a list of integers. This list is
    then returned as a phenotype
    '''

    def __init__(self, k=8):
        self.k = k

    def develop(self, individual):
        '''
        Develop method transforms a binary vector genotype to a integer phenotype. The
        objects k variable decide how the the binary vector should be split into integers.
        '''
        p = individual.genotype_container.genotype
        integer_list = [self._tobin(p[i:i + self.k]) for i in range(0, len(p), self.k)]
        return IntegerPhenotype(np.array(integer_list))


    def _tobin(self, x):
        s = ""
        for n in x:
            s += str(n)
        return int(s, 2)

class BinToSymbolTranslator(AbstractTranslator):
    '''
    BinToSymbolTranslator takes a binary vector genotype and transform it to an integer phenotype by
    using gray decoding. This translator is also very suitable for integers, since a bit flip of the
    binary vector only increase or decrease the integer by 1.
    '''

    def __init__(self, s=4):
        self.nr_of_symbols = s
        self.b = math.ceil(math.log2(self.nr_of_symbols))#Gray bits to support nr of symbols

    def develop(self, individual):
        '''
        Develop split binary vector into sub vectors that are decoded using gray codes to a integer value.
        The s variable decide how many numbers or symbols are supported. The s variable also decide how
        long the sub vectors are.
        '''
        p = individual.genotype_container.genotype

        #Use gray encoding so that a bit change will not
        symbol_list = [(self._g2i(p[i:i + self.b]))%self.nr_of_symbols for i in range(0, len(p), self.b)]
        return IntegerPhenotype(np.array(symbol_list))

    def _g2i(self, l):
        return BinToSymbolTranslator._bin2int(BinToSymbolTranslator._gray2bin(l))

    @staticmethod
    def _gray2bin(bits):
        b = [bits[0]]
        for nextb in bits[1:]: b.append(b[-1] ^ nextb)
        return b

    @staticmethod
    def _bin2int(bits):
        i = 0
        for bit in bits:
            i = i * 2 + bit
        return i