from abc import ABCMeta, abstractmethod
import numpy as np
import sys
from config.configuration import Configuration


class FitnessEvaluatorFactory:
    DEFAULT = "default"

    @staticmethod
    def make_fitness_evaluator(genome_length, evaluator=DEFAULT):
        '''
        Factory method create object by the supplied string argument, evaluator.
        Configurations are also retrieved and supplied as a kwarg argument for the object.
        '''
        selected = Configuration.get()["fitness"][evaluator]
        config = selected["parameters"]
        return getattr(sys.modules[__name__], selected["class_name"])(genome_length, **config)


class AbstractFitnessEvaluator(metaclass=ABCMeta):
    '''
    All fitness evaluators must inherit from AbstractFitnessEvaluator, implement abstract methods and
    be registered in config.json to be acceptable as a fitness evaluator
    '''

    def __init__(self, genome_length, **kwargs):
        pass

    @abstractmethod
    def evaluate(self, individual):
        '''
        Evaluate must set the fitness of the individual.
        '''
        pass

    def evaluate_all(self, population):
        '''
        Convenience method for evaluating all individuals in the population list.
        '''
        for individual in population:
            individual.fitness = self.evaluate(individual)


class DefaultFitnessEvaluator(AbstractFitnessEvaluator):
    #TODO: Rename to OneMax
    '''
    One max fitness evaluator. Heuristic that measure how similar a bit vector is to
    a target vector. The target vector defaults to containing just 1's, and therefore called the
    One max problem.
    '''


    def __init__(self, genome_length, random_target=False):
        if random_target:
            self.target = np.random.randint(2, size=genome_length)
            print("RANDOM TARGET: ", self.target)
        else:
            self.target = np.ones(genome_length, dtype=np.int)

    def evaluate(self, individual):
        '''
        Return the fraction of where the phenotype correspond to the target vector.
        Use not xor --> ==
        '''
        p = individual.phenotype_container.phenotype
        d = sum(p[i] == self.target[i] for i in range(p.size))
        return (d / p.size)


class LeadingFitnessEvaluator(AbstractFitnessEvaluator):
    '''
    For LOLZ prefix problem. Heuristic that prefer either long leading zeroes or leading ones. It will
    make the EA maximize leading zeroes (LZ) or leadning ones (LO). The big twist is that LZ is capped to recieve
    a max score of z.
    '''

    def __init__(self, genome_length, z=4):
        '''
        Optional argument z decide the cutoff for leading zeroes.
        '''
        self.z = z

    def evaluate(self, individual):
        '''
        Set's the fitness variable for the individual supplied as a argument. Phenotype extracted from individual,
        and length of the prefix is found. If the zeroes prefix is larger than z, its capped to z. Leading ones has no
        such cap.
        '''
        p = individual.phenotype_container.phenotype
        leading = p[0]
        score = 0
        for n in p:
            if n == leading:
                score += 1
            else:
                break
        if leading == 1:
            return score
        else:
            if score > self.z:
                return self.z
            return score


class SurprisingFitnessEvaluator(AbstractFitnessEvaluator):
    '''
    For Surprising sequence problem. Fitness can evaluate both globally and locally. Set to global as a default.
    Suprising fitness evaluator is a heuristic that tries to minimize errors and find a surprising sequence.
    A surprising sequence is a sequence where there exist no more than 1 occurrence of symbol A and B with distance d.
    '''

    def __init__(self, genome_length, locally=False):
        '''
        Optional parameter locally decide how the evaluate method behaves.
        With locally set to true evaluate will only consider distance's of 0.
        With locally set to false all distances are evaluated.
        '''
        self.locally = locally

    def evaluate(self, individual):
        '''
        Evaluate calculate fitness and store it in the individuals fitness variable.
        Phenotype of individual evaluated, depending on the locally variable.
        If locally is set to true symbols with no symbols inbetween will be considered.
        The function keeps track of errors that keep the sequence from being surprising, and return
        1- errors/possible_errors
        '''
        p = individual.phenotype_container.phenotype

        if self.locally:
            total = len(p)-1
            iteration = 2
        else:
            iteration =len(p)
            total = ((len(p)-1)*(len(p))/2)

        #Penality for nr of not surprising errors
        errors = 0
        for k in range(1, iteration):
            found_sequences = {}
            for i in range(len(p)-k):

                seq = str(p[i]) + "," + str(p[i+k])
                if seq in found_sequences:
                    errors += 1
                else:
                    found_sequences[seq] = (i, i+k)


        score = 1 - errors/total
        #score = 1/(1.+errors)
        return score
