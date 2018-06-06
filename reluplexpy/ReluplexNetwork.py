from . import ReluplexCore
import numpy as np

class ReluplexNetwork:
    """
    Abstract class representing general Reluplex network
    Defines functions common to ReluplexNetworkNnet and ReluplexNetworkTF
    """
    def __init__(self):
        """
        Constructs a ReluplexNetwork object and calls function to initialize
        """
        self.clear()
    
    def clear(self):
        """
        Reset values to represent empty network
        """
        self.numVars = 0
        self.equList = []
        self.reluList = []
        self.lowerBounds = dict()
        self.upperBounds = dict()
        self.inputVars = np.array([])
        self.outputVars = np.array([])
    
    def getNewVariable(self):
        """
        Function to request allocation of new variable
        
        Returns:
            varnum: (int) representing new variable
        """
        self.numVars += 1
        return self.numVars - 1
    
    def addEquation(self, x):
        """
        Function to add new equation to the network
        Arguments:
            x: (ReluplexUtils.Equation) representing new equation
        """
        self.equList += [x]
    
    def setLowerBound(self, x, v):
        """
        Function to set lower bound for variable
        Arguments:
            x: (int) variable number to set
            v: (float) value representing lower bound
        """
        self.lowerBounds[x]=v
    
    def setUpperBound(self, x, v):
        """
        Function to set upper bound for variable
        Arguments:
            x: (int) variable number to set
            v: (float) value representing upper bound
        """
        self.upperBounds[x]=v

    def addRelu(self, v1, v2):
        """
        Function to add a new Relu constraint
        Arguments:
            v1: (int) variable representing input of Relu
            v2: (int) variable representing output of Relu
        """
        self.reluList += [(v1, v2)]

    def lowerBoundExists(self, x):
        """
        Function to check whether lower bound for a variable is known
        Arguments:
            x: (int) variable to check
        """
        return x in self.lowerBounds

    def upperBoundExists(self, x):
        """
        Function to check whether upper bound for a variable is known
        Arguments:
            x: (int) variable to check
        """
        return x in self.upperBounds

    def participatesInPLConstraint(self, x):
        """
        Function to check whether variable participates in any piecewise linear constraint in this network
        Arguments:
            x: (int) variable to check
        """
        # ReLUs
        if self.reluList:
            fs, bs = zip(*self.reluList)
            if x in fs or x in bs:
                return True

    def getReluplex(self):
        """
        Function to convert network into Reluplex object
        Returns:
            reluplex: (ReluplexCore.Reluplex) representing query we want to solve with Reluplex
        """
        constantVar = self.numVars
        reluplex = ReluplexCore.Reluplex(self.numVars+1)
        
        #print("Initialize Cells")
        for e in self.equList:
            for (c, v) in e.addendList:
                assert v < self.numVars
                #print(e.auxVar,v,c)
                reluplex.initializeCell(e.auxVar,v,c)
            reluplex.markBasic(e.auxVar)
            reluplex.initializeCell(e.auxVar,constantVar,e.scalar)
            #print(e.auxVar,constantVar,e.scalar)
        
        #print("Relus:")
        for r in self.reluList:
            assert r[1] < self.numVars and r[0] < self.numVars
            reluplex.setReluPair(r[0], r[1]);
            #reluplex.setLowerBound(r[1], 0.0);
            #print(r[0],r[1])

        #print("Lower Bounds")
        for l in self.lowerBounds:
            assert l < self.numVars
            reluplex.setLowerBound(l, self.lowerBounds[l])
            #print(l,self.lowerBounds[l])
            
        #print("Upper Bounds")

        for u in self.upperBounds:
            assert u < self.numVars
            reluplex.setUpperBound(u, self.upperBounds[u])
            #print(u,self.upperBounds[u])
        
        reluplex.setLowerBound( constantVar, 1.0 );
        reluplex.setUpperBound( constantVar, 1.0 );
        
        return reluplex

    def solve(self, filename="", verbose=True):
        """
        Function to solve query represented by this network
        Arguments:
            filename: (string) path to redirect output to
            verbose: (bool) whether to print out solution
        Returns:
            vals: (dict: int->float) empty if UNSAT, else SATisfying solution
            stats: (Statistics) a Statistics object as defined in Reluplex,
                    it has multiple methods that provide information related
                    to how an input query was solved.
        """
        reluplex = self.getReluplex()
        vals = ReluplexCore.solve(reluplex, filename)
        #vals = {}
        if verbose:
            if len(vals)==0:
                print("UNSAT")
            else:
                print("SAT")
                for i in range(self.inputVars.size):
                    print("input {} = {}".format(i, vals[self.inputVars.item(i)]))

                for i in range(self.outputVars.size):
                    print("output {} = {}".format(i, vals[self.outputVars.item(i)]))

        return vals

    def evaluateWithReluplex(self, inputValues, filename="evaluateWithReluplex.log"):
        """
        Function to evaluate network at a given point using Reluplex as solver
        Arguments:
            inputValues: (np array) representing input to network
            filename: (string) path to redirect output
        Returns:
            outputValues: (np array) representing output of network
        """
        inputVars = self.inputVars
        outputVars = self.outputVars
        
        inputDict = dict()
        assignList = zip(inputVars.reshape(-1), inputValues.reshape(-1))
        for x in assignList:
            inputDict[x[0]] = x[1]

        reluplex = self.getReluplex()
        for k in inputDict:
            reluplex.setLowerBound(k, inputDict[k])
            reluplex.setUpperBound(k, inputDict[k])

        outputDict = ReluplexCore.solve(reluplex, filename)
        outputValues = outputVars.reshape(-1).astype(np.float64)
        for i in range(len(outputValues)):
            outputValues[i] = outputDict[outputValues[i]]
        outputValues = outputValues.reshape(outputVars.shape)
        return outputValues

    def evaluate(self, inputValues, useReluplex=True):
        """
        Function to evaluate network at a given point
        Arguments:
            inputValues: (np array) representing input to network
            useReluplex: (bool) whether to use Reluplex solver or TF/NNet
        Returns:
            outputValues: (np array) representing output of network
        """
        if useReluplex:
            return self.evaluateWithReluplex(np.array(inputValues))
        if not useReluplex:
            return self.evaluateWithoutReluplex(np.array(inputValues))

    def findError(self, inputs):
        """
        Function to find error between Reluplex solver and TF/Nnet at a given point
        Arguments:
            inputs: (np array) representing input to network
        Returns:
            err: (np array) representing error in each output variable
        """
        outReluplex = self.evaluate(inputs, useReluplex=True)
        outNotReluplex = self.evaluate(inputs, useReluplex=False)
        err = np.abs(outReluplex - outNotReluplex)
        return err
