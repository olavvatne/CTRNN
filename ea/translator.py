from abc import ABCMeta, abstractmethod
import sys

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


class BinToWeightTranslator(AbstractTranslator):
    '''
    BinToIntTranslator takes a binary vector genotype and transform it to an integer phenotype by
    using gray decoding. This translator is also very suitable for integers, since a bit flip of the
    binary vector only increase or decrease the integer by 1.
    '''

    def __init__(self, k=8):
        self.k = k

    def develop(self, individual):
        '''
        Develop split binary vector into sub vectors that are decoded using gray codes to a integer value.
        The k variable decide the number granularity.
        '''
        #TODO: Integer for now, should probably be between 0-1 or -1 or 1.
        p = individual.genotype_container.genotype

        #Use gray encoding so that a bit change will not
        phenotype = [(self._g2i(p[i:i + self.k])) for i in range(0, len(p), self.k)]
        return IntegerPhenotype(np.array(phenotype))


    def _g2i(self, l):
        return BinToWeightTranslator._bin2int(BinToWeightTranslator._gray2bin(l))

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