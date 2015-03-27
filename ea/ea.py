import numpy as np

from ea.genotype import GenotypeFactory
from ea.translator import TranslatorFactory
from ea.evaluator import FitnessEvaluatorFactory
from ea.individual import Individual
from ea.selection import AdultSelectionFactory
from ea.reproduction import ParentSelectionFactory


class EA(object):
    #Highly parameterized, should be able to change all parameters, through gui
    #Create python file with methods that return object, with the right mix of fitness eval, phenotype etc, can be used
    #a setup type of method that configure the EA before running. Drop down with alternatives in gui, pop size etc d
    #decided by other gui elements

    EVENT_RATE = 10

    def __init__(self):
        self.is_stopping = False
        self.translator = None
        self.fitness_evaluator = None
        self.genotype = None
        self.genome_length = 0
        self.phenotype = None
        self.adult_selector = None
        self.parent_selector = None
        self.listener = None
        self.adult_pool = []

    def add_listener(self, listener):
        '''
        The EA will during the run send updates containing best fitness average fitness etc.
        A listner can be supplied to the object that will receive these updates. Currently only AppUI that
        contain functions neccessary.
        '''
        self.listener = listener

    def run(self, population_size, cycles, fitness_threshold):
        '''
        Run will run the actual evolutionary algorithm. The number of generations or cycles, stopping condition
        and inital population size are decided by the method arguments.

        A basic generation loop consist of:
        -Development of children. (Construct a phenotype from their genotype)
        -Evaluate developed children's fitness
        -Select who should participate in the adult pool. (All other individuals die off)
        -Select mating pairs (Who get to reproduce. Sexual reproduction so mate pool consist of tuples)
        -Create children. (Mutation and crossover)
        -Send update to GUI (every 10th cycle)
        '''
        print("-------------------------")
        self.is_stopping = False

        if not self.is_legal():
            raise RuntimeError("Cannot run EA. Lack necessary objects")

        children = self.create_population(population_size)  #Inital population
        self.adult_pool = children

        for c in range(cycles):

            self.geno_to_pheno_development(children)
            self.fitness_evaluator.evaluate_all(children)
            self.adult_pool = self.adult_selector.select(self.adult_pool, children, population_size)
            mating_adults = self.parent_selector.select_mating_pool(self.adult_pool, population_size, t=1-(c/cycles))
            children = self.reproduce(mating_adults)
            #TODO: CORRECT ELITISM IMPLEMENTATION. FITNESS REEVALUATED?
            children.append(self.adult_selector.best)
            self.adult_pool.append(self.adult_selector.best)

            #Check stopping condition, and gui update below
            self.best_individual = max(self.adult_pool, key=lambda a: a.fitness)
            if self.is_stopping or fitness_threshold <=  self.best_individual.fitness:
                break

            if self.listener and c%EA.EVENT_RATE == 0:
                #Sends an update every 10th cycle. Fraction multiplied by 100 and 10 (10th cyle)
                #send to indicate evolution loop progression.
                self.send_update(c, cycles,  self.best_individual)

        #Final update
        self.best_individual = max(self.adult_pool, key=lambda a: a.fitness)
        self.send_update(c+1, cycles, self.best_individual)
        return self.best_individual
        print("-------------------------")

    def stop(self):
        '''
        Calling stop will stop an EA in progress. Will stop the ea loop.
        '''
        self.is_stopping = True

    def send_update(self, c, cycles, best):
        '''
        Summary information for cycle c, and send to the listner's update function. (AppUI)
        Sends:
        -Cycle the EA is currently working on
        -Generations since last update
        -Average fitness of the population
        -Best fitness of the population
        -Standard deviation of the population
        '''
        avg_fitness = sum(individual.fitness for individual in self.adult_pool)/len(self.adult_pool)
        std = np.std(list(a.fitness for a in self.adult_pool))
        print("C: ", c, "B_f: ", best.fitness, " A_f: ", avg_fitness, " std: ", std, "P: ", best.phenotype_container)
        self.listener.update(c, 1/cycles * 100 * EA.EVENT_RATE, avg_fitness, best.fitness, std)

    def create_population(self, n):
        '''
        Create's an initial population. An individual's genotype is created and retrieved from
        GenoTypeFactory. The genotype is initalized to a completely random genome.
        '''
        population = []
        for i in range(n):
            genotype = GenotypeFactory.make_fitness_genotype(self.genotype)
            genotype.init_random_genotype(self.genome_length)
            individual = Individual(genotype, self.translator)
            population.append(individual)
        return population

    def geno_to_pheno_development(self, children):
        '''
        Develop all individual's in the children list, which means that a phenotype is created for
        all children in the list.
        '''
        for individual in children:
            individual.devlop()

    def reproduce(self, mating_adults):
        '''
        Reproduce returns a list of children, created by the mating adults. Mating_adults argument contain
        tuples of two individuals selected to mate by the reproduction parent selector. Each mating produce
        2 children, which is extended to the children list.
        '''
        children = []
        for a1, a2 in mating_adults:
            children.extend(a1.mate(a2))
        return children

    def setup(self, geno_to_pheno, evaluator, geno, adult, parent, genome_length):
        '''
        This EA is highly parameterized, and setup help keep it this way. User supply strings that decide what
        type of translator, evaluator, genotype, adult selection and parent selection. Different factories are
        then used to initialize object's corresponding to the user's choice's.
        '''
        self.translator = TranslatorFactory.make_fitness_translator(geno_to_pheno)
        self.fitness_evaluator = FitnessEvaluatorFactory.make_fitness_evaluator(genome_length, evaluator)
        self.genotype = geno
        self.genome_length = genome_length
        self.adult_selector = AdultSelectionFactory.make_adult_selector(adult)
        self.parent_selector = ParentSelectionFactory.make_parent_selector(parent)

    def is_legal(self):
        '''
        Checks that the EA have initialized objects of all required modules, like adult selection, parent selection,
        fitness evaluator and translator.
        '''
        return self.translator and self.fitness_evaluator and self.adult_selector and self.parent_selector

