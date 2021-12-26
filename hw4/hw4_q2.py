from gurobipy import *
import numpy as np

import data_1 as data

#import data from file
h = data.h
c = data.c
d = data.service_time
no_show = data.no_show

T = data.T
max_doc = data.K

doctors = data.doctors
patients = data.patients
scenarios = data.scenarios

lam = 100
alpha = 0.1

#build model
m = Model('telemedicine')
m.modelSense = GRB.MINIMIZE
m.Params.outputFlag = 0

#add variables
x = m.addVars(doctors, vtype=GRB.BINARY, obj=h)

y = tupledict()
for k in scenarios:
    for j in doctors:
        for i in patients:
            y[(i,j,k)] = m.addVar(vtype=GRB.BINARY, obj=c[(i,j)]/len(scenarios))
            
u = m.addVar(vtype=GRB.CONTINUOUS, lb=-GRB.INFINITY, ub=GRB.INFINITY, obj=lam)

w = m.addVars(scenarios, obj=lam/(1-alpha)/len(scenarios))

#add constraints
m.addConstr(x.sum() <= max_doc)
m.addConstrs(quicksum(y[(i,j,k)] for j in doctors) == no_show[(k,i)] for i in patients for k in scenarios)
m.addConstrs(quicksum(d[(k,i)] * y[(i,j,k)] for i in patients) <= T*x[j] for j in doctors for k in scenarios)
m.addConstrs(w[k] >= quicksum(h[j]*x[j] for j in doctors) 
             + quicksum(c[(i,j)]*y[(i,j,k)] for i in patients for j in doctors) - u for k in scenarios)

m.optimize()
doc_list = [j for j in doctors if x[j].x > 0.999]

print('lambda = ', lam)
print('objective value = ', m.objval)
print('selected doctors: ', doc_list)