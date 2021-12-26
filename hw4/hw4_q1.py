from gurobipy import *
import random
import numpy
import math
from scipy.stats import poisson

numpy.random.seed(1612)

numscen = 30 # N
numbatch = 10  # M
numeval = 500 # N_tilde

candx = 0.0

### function for building and solving the extensive form for a given sample xi (in vector)
### returns the objective value and the solution
def solveEF(xi):

    ef = Model("extensiveform")
    ef.params.logtoconsole=0
    x = ef.addVar(obj=-0.75, lb=0.0, ub=5.0)
    v1 = {}
    v2 = {}
    v3 = {}
    v4 = {}
    for j in range(numscen):
        v1[j] = ef.addVar(obj=-1/float(numscen))
        v2[j] = ef.addVar(obj=3/float(numscen))
        v3[j] = ef.addVar(obj=1/float(numscen))
        v4[j] = ef.addVar(obj=1/float(numscen))

    ef.update()

    for j in range(numscen):
        ef.addConstr(-v1[j]+v2[j]-v3[j]+v4[j] == xi[j] + x/2)
        ef.addConstr(-v1[j]+v2[j]+v3[j]-v4[j] == 1 + xi[j] + x/4)

    ef.modelSense = GRB.MINIMIZE
    ef.update()
    ef.optimize()
    return [ef.objval, x.x]

### function for building and solving the second stage problem for
#### a given value xi and first-stage solution x
### returns the objective value
def solveSSP(xval, xi):
    
    ssp = Model('second_stage')
    ssp.params.logtoconsole=0
    ssp.modelSense = GRB.MINIMIZE
    
    v = ssp.addVars(range(4), obj=[-1,3,1,1])
    ssp.addConstr(-v[0]+v[1]-v[2]+v[3] == xi + xval/2)
    ssp.addConstr(-v[0]+v[1]+v[2]-v[3] == 1 + xi + xval/4)
    ssp.optimize()

    return -0.75*xval + ssp.objval

### estimate LB
#numpy arrays to store the history of objvals and solutions
objvals = numpy.zeros(numbatch)
xvals = numpy.zeros(numbatch)

for k in range(numbatch): # M

    ### set up and solve extensive form for a sample average approximation problem
    xi = poisson.rvs(0.5, size=numscen)  # creates numscen scenarios, N
    [objvals[k],xvals[k]] = solveEF(xi)

print(objvals)

print('mean SAA objval = ', numpy.mean(objvals))
print('stdev of SAA objval = ', numpy.std(objvals))
lbmean = numpy.mean(objvals)
lbwidth = numpy.std(objvals)/math.sqrt(numbatch)*2.262 #t-value for df=9

### estimate UB using the candidate solution with the best objective value

candx = xvals[numpy.argmax(objvals)]
print(' ')
print('candidate solution = ', candx)
evalvals = numpy.zeros(numeval)
xi = poisson.rvs(0.5, size=numeval)
for k in range(numeval):
    evalvals[k] = solveSSP(candx,xi[k])
    
print('mean solution objval = ', numpy.mean(evalvals))
print('stdev of solution objval = ', numpy.std(evalvals))
ubmean = numpy.mean(evalvals)
ubwidth = numpy.std(evalvals)/math.sqrt(numeval)*1.96

print(' ')
print('ci on lower bound = [', round(lbmean-lbwidth,2), ',', round(lbmean+lbwidth,2), ']')
print('ci on upper bound = [', round(ubmean-ubwidth,2), ',', round(ubmean+ubwidth,2), ']')

WorstLB = lbmean-lbwidth
WorstUB = ubmean+ubwidth
print('worst gap = [', round(WorstLB,2), ',', round(WorstUB,2), ']')
print('worst gap % = ', round(100.0*(WorstUB-WorstLB)/WorstUB,2))