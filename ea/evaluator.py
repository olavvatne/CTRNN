from abc import ABCMeta, abstractmethod
import sys

import numpy as np

from config.configuration import Configuration
from simulator.environment import Environment


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
        #TODO: should individual have it's own ann or weights added to ann here?

        d = np.sum(np.logical_not(np.logical_xor(p, self.target), dtype=np.bool))
        return (d / p.size)


class TrackerAgentFitnessEvaluator(AbstractFitnessEvaluator):
    '''

    '''

    def __init__(self,genome_length, test=1):
        #TODO: Fix parameters, and initialize environment the agent should be tested on
        self.scenario = Environment(30,15)

    def evaluate(self, individual):
        '''

        '''
        p = individual.phenotype_container.get_ANN()
        avoidance, capture, failure = self.scenario.score_agent(p)
        #TODO: Make a scoring for tracker
        return capture/40 #The maximum amount of captures