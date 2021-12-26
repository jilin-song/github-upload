from gurobipy import *
import numpy as np

'''
Stochastic Programming Solution
'''

#model parameters

space = [0.5, 1, 2]
profit = [0.5, 1, 3]
capacity = 50

prob = [0.3, 0.3, 0.2, 0.1, 0.1]

demand = [[25, 30, 10],
          [26, 26, 12],
          [18, 35, 18],
          [24, 32, 12],
          [15, 15, 15]]

y_obj = [[i*j for j in profit] for i in prob]

#range object for the three types of planes
planes = range(len(space))

#range object for scenarios
scenario = range(len(prob))

#build model
m = Model('Partitioning Problem')

x = m.addVars(planes, vtype=GRB.INTEGER, name='x')
y = m.addVars(scenario, planes, vtype=GRB.INTEGER, obj=y_obj, name='y')

m.modelSense = GRB.MAXIMIZE

#constraints

#capacity constraint
m.addConstr(sum(x[i]*space[i] for i in planes) <= capacity)

#prohibit oversale
m.addConstrs(y[k,i]-x[i] <= 0 for k in scenario for i in planes)

#demand constraint
m.addConstrs(y[k,i]<=demand[k][i] for k in scenario for i in planes)

m.optimize()

x_val = [x[i].x for i in planes]
y_val = np.array([[y[k,i].x for i in planes] for k in scenario])
obj_sp = m.ObjVal
print(obj_sp)
print(x_val)
print(y_val)

