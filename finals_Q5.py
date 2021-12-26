from gurobipy import *
import random
import numpy as np
import math

pairs = [(i,j) for i in range(1,51) for j in range(1,51) if i!=j]

random.seed(111)

numscen = 50 # N
numbatch = 15  # M
numeval = 10000 # N_tilde

#function to solve extensive forms
def solveEF(demand):
    ef = Model()
    ef.params.logtoconsole=0
    x = ef.addVars(pairs, obj=-5)
    
    for s in range(num_scen):
        y[s] = ef.addVars(pairs, obj=10/float(num_scen)) #I don't have the time to do the q coefficient
    
    ef.addConstrs()
    
    ef.modelSense = GRB.MINIMIZE
    ef.update()
    ef.optimize()
    return [ef.objval, x]

    
#function to solve 2nd-stage problems
def solveSSP(xval, demand):
    return

#estimate LB
for k in range(numbatch): # M

    ### set up and solve extensive form for a sample average approximation problem
    demand = np.random.normal(4, 1, numscen)  # creates numscen scenarios, N
    [objvals[k],xvals[k]] = solveEF(demand)

print(objvals)

#estimate UB

#sorry I ran out of time