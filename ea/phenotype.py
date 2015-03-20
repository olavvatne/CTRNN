

class AbstractPhenotype(object):
    '''
    Simply phenotype object. Genotype to phenotype translator decide what subclass will be used.
    '''

    def __init__(self):
        pass

class IntegerPhenotype(AbstractPhenotype):
    '''
    Integer phenotype. Treated as the default phenotype. In most cases this is enough for
    a problem.
    '''
    def __init__(self, phenotype):
        self.phenotype = phenotype

    def __repr__(self):
        return str(self.phenotype)