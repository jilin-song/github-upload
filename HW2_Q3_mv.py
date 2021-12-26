from gurobipy import *
import numpy as np

'''
Mean Value Approach
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

#calculate mean demands
demand_mv = [sum(demand[k][i]*prob[k] for k in scenario) for i in planes]

#build model to solve for x_mv
m = Model('Partitioning Problem_mv')

x = m.addVars(planes, vtype=GRB.INTEGER, name='x')
y = m.addVars(planes, vtype=GRB.INTEGER, obj=profit, name='y')

m.modelSense = GRB.MAXIMIZE

#constraints

#capacity constraint
m.addConstr(sum(x[i]*space[i] for i in planes) <= capacity)

#update these 2 constraints
#prohibit oversale
m.addConstrs(y[i]-x[i] <= 0 for i in planes)

#demand constraint
m.addConstrs(y[i]<=demand_mv[i] for i in planes)

m.optimize()

x_val = [x[i].x for i in planes]
y_val = [y[i].x for i in planes]
print(x_val)
print(y_val)


#new model to evaluate x_mv
m = Model('Partitioning Problem_mv_evaluation')

#x = m.addVars(planes, vtype=GRB.INTEGER, name='x')
y = m.addVars(scenario, planes, vtype=GRB.INTEGER, obj=y_obj, name='y')

m.modelSense = GRB.MAXIMIZE

#constraints

#capacity constraint (not needed)
#m.addConstr(sum(x[i]*space[i] for i in planes) <= capacity)

#prohibit oversale (x_val is a parameter here)
m.addConstrs(y[k,i] <= x_val[i] for k in scenario for i in planes)

#demand constraint
m.addConstrs(y[k,i]<=demand[k][i] for k in scenario for i in planes)

m.optimize()
y_val = np.array([[y[k,i].x for i in planes] for k in scenario])
obj_mv = m.ObjVal
print(y_val)

from HW2_Q3 import obj_sp
vss = obj_sp - obj_mv

print('The VSS is {:.2f} units of profit from medium-sized planes'.format(vss))