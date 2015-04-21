from abc import ABCMeta, abstractmethod
import numpy as np
import random, math, sys
from config.configuration import Configuration

class ParentSelectionFactory:
    PROPORTIONATE = "proportionate"

    @staticmethod
    def make_parent_selector(selector=PROPORTIONATE, config=None):
        '''
        Factory method create object by the supplied string argument, selector.
        Configurations are also retrieved and supplied as a kwarg argument for the object.
        '''
        if not config:
            selected = Configuration.get()["parent_selection"][selector]
        else:
            selected = config["parent_selection"][selector]
        config = selected['parameters']
        return getattr(sys.modules[__name__], selected["class_name"])(**config)


class AbstractParentSelection(metaclass=ABCMeta):
    '''
    All parent selectors must inherit from AbstractParentSelection, implement select_mating_pool and
    be registered in config.json to be acceptable as a parent selector.
    To be a valid subclass, select_mate_pool must return a list containing tuples of two individuals
    selected to mate.
    '''
    @abstractmethod
    def select_mating_pool(self, adults, m):
        pass

    def _global_weighted_select(self, population, probs,  m):
        '''
        Roulette wheel selection. Returns a list of tuples of selected parents. The list contains
        m/2 tuples. All selections are weighted by the probability list, probs.
        '''
        return np.split(np.random.choice(population, size=m, p=probs, replace=True), m/2)
        #return[np.random.choice(population, size=2, p=probs, replace=False) for i in range(int(m/2))]
        #Old way. Will not let ind mate with itself, but very small chance and big increase in speed



class ParentFitnessProportionateSelection(AbstractParentSelection):
    '''
    Proportionate selection scale the roulette wheel by fitness only. A high performing individual
    will have a bigger portion of the wheel, and will most likely reproduce more than once.
    '''

    def select_mating_pool(self, population, m, t=1):
        '''
        Probabilties for an individual reproducing is Individual(fitness)/Population(avg-fitness)
        Returns a list of tuples where each contain two individuals matched for reproduction
        '''
        fitness = list(adult.fitness for adult in population)
        total = sum(fitness)
        probs = list(f/total for f in fitness)
        return self._global_weighted_select(population, probs, m)


class ParentSigmaScalingSelection(AbstractParentSelection):
    '''
    Sigma scaling selection use the standard deviation of the poputation to scale the probabilites.
    Modifies the selection pressure. Reduce selection pressure if few individuals are much better or worse, and
    increase selection pressure when a population has become homogeneous.
    '''

    def select_mating_pool(self, population, m, t=1):
        '''
        For every individual 1 + (I(f) - P(avg_f))/2*P(std) is calculated.
        If value is below zero, a small positive constant is given so the individual has some probability
        of being chosen. The numbers are then normalized and used as probabilities for the weighted
        selection.
        '''
        fitness_list = list(a.fitness for a in population)
        avg = sum(fitness_list)/len(population)
        std = max(0.0001, np.std(fitness_list))
        exp_values = list((1+((f -avg)/(2*std))) for f in fitness_list)

        for i, v in enumerate(exp_values):
            if v <= 0:
                exp_values[i] = 1/len(population) #If negative expected value, reset to small positive value so the individual has
                #of getting picked
        s = sum(exp_values)
        probs = list(e/s for e in exp_values)
        return self._global_weighted_select(population, probs, m)


class ParentBoltzmannSelection(AbstractParentSelection):
    '''
    Boltzmann selection uses a temperature to gradually increase selection pressure. Help combat premature
    convergence and late stagnation. Dampens the probabilities of good individuals being selected early, and
    increase probabilities later.
    '''

    def select_mating_pool(self, population, m, t=1):
        '''
        Argument t is composed of a number between 0 and 1 that is calculated by how long the ea has run.
        exp_values contain a list of the temperature scaled fitness of each individual. These values are then
        normalized and used as probabilities for the weighted selection.
        '''
        l = population[0].genotype_container.genotype.size
        temp = list(math.exp(a.fitness/t) for a in population)
        avg = sum(temp)/len(population)
        exp_values = list(c/avg for c in temp)
        s = sum(exp_values)
        probs = list(e/s for e in exp_values)
        return self._global_weighted_select(population, probs, m)


class ParentTournamentSelection(AbstractParentSelection):
    '''
    Tournament selection construct K random groups of individuals which compete for spots in the
    mate pool. This selection can help combat high selection pressure, by increasing k or high e.
    '''

    def __init__(self, k=8, e=0.2):
        self.k = k
        self.e = e

    def select_mating_pool(self, population, m, t=1):
        '''
        K groups of adults created that compete for a slot in the mate pool. Tournaments are held where
        the best individual of the group are selected with a probability of 1-e. A random selection is done
        if not the best is selected. Method return a list of tuples, each containing two individuals.
        '''
        tournaments = [population[i:i + self.k] for i in range(0, len(population), self.k)]
        mate_pool = []
        for i in range(int(m/2)):
            t1 = self._conduct_tournament_selection(tournaments[(i)%len(tournaments)], self.e)
            t2 = self._conduct_tournament_selection(tournaments[(i)%len(tournaments)], self.e)
            mate_pool.append((t1, t2))
        return mate_pool

    def _conduct_tournament_selection(self, tournament, e):
        '''
        Conducts a local tournament. With probabilty 1-e is the best individual returned. Otherwise a random
        selection.
        '''
        n = random.random()
        if n < e:
            return random.choice(tournament)
        else:
            return max(tournament, key=lambda i: i.fitness)

