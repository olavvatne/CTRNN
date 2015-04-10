
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


class CTRNNParametersPhenotype(AbstractPhenotype):
    '''
    CTRNNParametersPhenotype. Will have access to ANN that can be configured with
    weights from the phenotype. Direct mapping, structure of ANN not evolvable, only
    weights are adjusted using this phenotype.
    '''
    def __init__(self, phenotype, ann):
        self.ann = ann
        self.phenotype = phenotype
        #TODO: Configure to match CTRNN

    def get_ANN(self):
        self.ann.set_weights(self.phenotype)
        return self.ann

    def __repr__(self):
        return str(len(self.phenotype))