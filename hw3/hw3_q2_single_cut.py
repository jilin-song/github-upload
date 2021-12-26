from gurobipy import *
import numpy as np
import time

CutViolationTolerance = 0.0001

import data as Data

cities = Data.cities # set of cities
scenarios = Data.scenarios # set of scenarios
theta = Data.theta # unit cost of delivering alcohol to city n in the first stage
theta_s = Data.theta_prime # unit cost of transporting alcohol between city n and CA in the second stage

h = Data.h # unit cost of unused alcohol in the inventory
g = Data.g # unit cost of shortage of alchohol
I = Data.I # inventory of CA at the beginning
Yn = Data.Yn # inventory of city n at the beginning
demand = Data.demand # demand of city n under scenario k
prob = 1.0/len(scenarios) # probability of scenario k

#function to modify and solve subproblem for each scenario
def ModifyAndSolveSP(k):
    # Modify constraint rhs
    CapacityConst.rhs = sum(xsol.values()) - I
    for i in cities:
        DemandConsts[i].rhs = demand[i,k] - xsol[i] - Yn[i]

    # Solve and get the DUAL solution
    SP.optimize()

    pi_sol = CapacityConst.Pi
    
    gamma_sol = {}
    for i in cities:
        gamma_sol[i] = DemandConsts[i].Pi

    SPobj = SP.objVal

    return SPobj, pi_sol, gamma_sol

#Build the Master Problem
MP = Model('MP')

MP.Params.outputFlag = 0 # turn off output

#first stage variables
x = MP.addVars(cities, obj=theta, name='x')
t = MP.addVar(obj=1.0, name='t') #the Q values are always non-negative according to the problem

MP.modelSense = GRB.MINIMIZE

#first stage constraint
MP.addConstr(x.sum()<=I)


#Build the primal Subproblem (for any scenario k)
SP = Model('SP')

SP.Params.outputFlag = 0

#second stage variables
v = SP.addVars(cities, obj=theta_s, name='v') # 'u_nc' variable -- alcohol transported from region n to CA
w = SP.addVars(cities, obj=theta_s, name='w') # 'u_cn' variable -- alcohol reallocated to region n from CA
z = SP.addVars(cities, obj=h, name='z') # excessive alcohol
s = SP.addVars(cities, obj=g, name='s') # alcohol shortage

SP.modelSense = GRB.MINIMIZE

CapacityConst = SP.addConstr(v.sum() - w.sum() >= 0) #initialize rhs (sum of xsol - I) as 0

DemandConsts = {}
for i in cities:
    DemandConsts[i] = SP.addConstr(w[i] + s[i] - z[i] - v[i] == 0)
    #initialize rhs (demand - xsol - Yn) as 0

##### Benders Loop #####
start = time.time()
CutFound = True
NoIters = 0
BestUB = GRB.INFINITY
n_cut_history = []
while (CutFound) and (NoIters<=199):
    NoIters += 1
    CutFound = False

    # Solve MP
    MP.update()
    MP.optimize()

    # Get MP solution
    MPobj = MP.objVal
    print('Iteration #: {}'.format(NoIters))
    print('MPobj: %g' % MPobj)

    xsol = dict(zip(cities, [x[i].x for i in cities]))
    tsol = t.x

    n_cut = 0
    Q_func = 0
    expr = LinExpr()

    for k in scenarios:
        Qvalue, pi_sol, gamma_sol = ModifyAndSolveSP(k)

        Q_func += prob * Qvalue #calculate the value aggregate Q function (calligraphic Q)
        
        expr.add((x.sum()-I)*pi_sol + quicksum((demand[i,k]-Yn[i]-x[i])*gamma_sol[i] for i in cities), mult=prob)
        #build the cut associated with each scenario

    if(tsol < Q_func - CutViolationTolerance):
        CutFound = True
        n_cut += 1
            
        MP.addConstr(t - expr >= 0) #add single cut

    UB = Q_func + sum([theta[i]*xsol[i] for i in cities])
    
    if(UB < BestUB):
        BestUB = UB
    
    n_cut_history.append(n_cut)
    print("UB: " + str(UB))
    print("BestUB: " + str(BestUB))
    print('# of cuts added: {} \n'.format(n_cut))
    
end = time.time()
time_taken = end - start
print('\nOptimal Solution:')
print('MPobj: %g' % MPobj)
print("xsol: " + str(xsol))
print("tsol: " + str(tsol))
print("NoIters: " + str(NoIters))
print('Total number of cuts: {}'.format(sum(n_cut_history)))
print('Total time taken: {}s'.format(time_taken))