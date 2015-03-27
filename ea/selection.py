from abc import ABCMeta, abstractmethod
import sys
from config.configuration import Configuration


class AdultSelectionFactory:
    FULL = "full"

    @staticmethod
    def make_adult_selector(selector=FULL):
        '''
        Factory method create object by the supplied string argument, selector.
        Configurations are also retrieved and supplied as a kwarg argument for the object.
        '''
        selections = Configuration.get()["adult_selection"]
        return  getattr(sys.modules[__name__], selections[selector]["class_name"])()


class AbstractAdultSelection(metaclass=ABCMeta):
    '''
    All adult selectors must inherit from AbstractAdultSelection, implement the select method and
    be registered in config.json to be acceptable as a adult selection class.
    '''
    def __init__(self):
        self.elitism = True
        #TODO: parameterize elitism
        self.best = None

    def set_best(self, adults):
        self.best = max(adults, key=lambda a: a.fitness)

    @abstractmethod
    def select(self, adults, children):
        pass


class FullReplacementAdultSelection(AbstractAdultSelection):
    '''
    All Adults from the previous generation are removed from the pool eligible for
    reproduction.
    '''

    def select(self, adults, children, m):
        self.set_best(adults)
        return children[:m]


class OverProductionAdultSelection(AbstractAdultSelection):
    '''
    Over-production create selection pressure by letting the n children compete for
    the m spots in the adult_pool. This require that more n > m.
    '''

    def select(self, adults, children, m):
        self.set_best(adults)
        adult_pool = sorted(children, key=lambda child:child.fitness, reverse=True)
        return adult_pool[:m]


class MixingAdultSelection(AbstractAdultSelection):
    '''
    Mixing selection lets both adults and children compete for the m spots in the adult_pool,
    and therefore creating selection pressure.
    '''

    def select(self, adults, children, m):
        self.set_best(adults)
        mix = adults + children
        adult_pool = sorted(mix, key=lambda individual:individual.fitness, reverse=True)
        return adult_pool[:m]


