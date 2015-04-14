from abc import ABCMeta, abstractmethod
import sys

import numpy as np

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
        return np.copy(individual.genotype_container.genotype)


class BinToParameterTranslator(AbstractTranslator):
    '''
    BinToParametersTranslator takes a binary vector genotype and transform it to an weight phenotype by
    using gray decoding. This translator is also very suitable for number parameters, since a bit flip of the
    binary vector only increase or decrease the weight by a small amount.
    '''

    def __init__(self, k=8):
        '''
        The init use arguments from configuration that tells how many bits to use per parameter. For example 8 bits will
        give 256 values between 0 and 1. Layers is a list instructing the ANN of how many neurons per layer. There has to
        be at least to layers. Input and output. A user determined number of hidden layers can be used.
        '''
        #TODO: Different parameters have different ranges. Fix by parameter and the
        self.k = k
        self.nr_of_values = 2**k


    def develop(self, individual):
        '''
        Develop split binary vector into sub vectors that are decoded using gray codes to a integer value.
        The k variable decide the number granularity. The integer is then divided by the total number of values
        supported by the bit length.
        '''

        #Use gray encoding so that a bit change will not
        p = individual.genotype_container.genotype
        parameters = [self._g2i(p[i:i + self.k])/self.nr_of_values for i in range(0, len(p), self.k)]

        return parameters




    def _g2i(self, l):
        return BinToParameterTranslator._bin2int(BinToParameterTranslator._gray2bin(l))

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