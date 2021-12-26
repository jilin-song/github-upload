from gurobipy import *
import numpy as np

'''
Perfect information
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

#y_obj = [[i*j for j in profit] for i in prob]

demand_pi = [0, 0, 0]

#range object for the three types of planes
planes = range(len(space))

#range object for scenarios
scenario = range(len(prob))

#build model to solve for x_mv
m = Model('Partitioning Problem_pi')

x = m.addVars(planes, vtype=GRB.INTEGER, name='x')
y = m.addVars(planes, vtype=GRB.INTEGER, obj=profit, name='y')

m.modelSense = GRB.MAXIMIZE

#constraints

#capacity constraint
m.addConstr(sum(x[i]*space[i] for i in planes) <= capacity)

#prohibit oversale
m.addConstrs(y[i]-x[i] <= 0 for i in planes)

#demand constraint
constr_demand = m.addConstrs(y[i]<=demand_pi[i] for i in planes)

obj_vals = []

#solve |K| many optimization problems and collect their optimal objective values
for k in scenario:
    m.remove(constr_demand)
    demand_pi = demand[k]
    constr_demand = m.addConstrs(y[i]<=demand_pi[i] for i in planes)
    m.update()
    m.optimize()
    obj_vals.append(m.ObjVal)

print(obj_vals)
obj_pi = sum(obj_vals[k]*prob[k] for k in scenario)

from HW2_Q3 import obj_sp
evpi = obj_pi - obj_sp

print('The EVPI is {:.2f} units of profit from medium-sized planes'.format(evpi))