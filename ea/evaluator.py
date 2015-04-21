from abc import ABCMeta, abstractmethod
import sys

import numpy as np
from config.configuration import Configuration
from simulator.agent import Simulator


class FitnessEvaluatorFactory:
    DEFAULT = "default"

    @staticmethod
    def make_fitness_evaluator(genome_length, evaluator=DEFAULT, config=None):
        '''
        Factory method create object by the supplied string argument, evaluator.
        Configurations are also retrieved and supplied as a kwarg argument for the object.
        '''
        if not config:
            selected = Configuration.get()["fitness"][evaluator]
        else:
            selected = config["fitness"][evaluator]
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

    def evaluate_all(self, population, cycle):
        '''
        Convenience method for evaluating all individuals in the population list.
        '''

        for individual in population:
            individual.fitness = self.evaluate(individual, cycle)


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

    def evaluate(self, individual, cycle):
        '''
        Return the fraction of where the phenotype correspond to the target vector.
        Use not xor --> ==
        '''
        p = individual.phenotype_container

        d = np.sum(np.logical_not(np.logical_xor(p, self.target), dtype=np.bool))
        return (d / p.size)


class TrackerAgentFitnessEvaluator(AbstractFitnessEvaluator):
    '''

    '''

    def __init__(self,genome_length, pull=False, wrap=True, avoidance=True):
        self.wrap = wrap
        self.pull = pull
        self.is_avoidance = avoidance
        self.simulator = Simulator(pull=pull, wrap=wrap)


    def evaluate(self, individual, cycle, debug=False):
        '''
        Depending on config settings, the score for an individual is
        calculated differently.
        '''
        p = individual.phenotype_container
        self.simulator.set(p)
        capture, avoidance, failure_capture, failure_avoidance, speed_rate, explore_rate, pull_rate = self.simulator.run(p)
        capture_rate = capture/(capture+failure_capture)
        avoidance_rate =avoidance/(avoidance+failure_avoidance)
        turnon = min(20, cycle)/20

        score = (4.0*capture_rate) - 4*(abs(speed_rate - 0.28))
        if self.is_avoidance:
            score += 2.0*avoidance_rate
        if not self.wrap:
            score += ((1.0-turnon)*speed_rate) + (4.0*explore_rate**2) + (4.0*capture_rate)
        if self.pull:
            score += (3*pull_rate)# + (speed_rate)

        if(debug):
            print("----------")
            print(turnon)
            print("Cap: ","{0:.2f}".format(capture_rate), "Avo: ","{0:.2f}".format(avoidance_rate), "Spe: ", "{0:.5f}".format(speed_rate), "pulls", "{0:.5f}".format(pull_rate), "explore", explore_rate)
        return score