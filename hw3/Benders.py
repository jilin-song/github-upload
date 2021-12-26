from gurobipy import *
import numpy as np

##### Building the Data #####

# Read the data from file
import BendersData as Data

CutViolationTolerance = 0.0001
OptionForSubproblem = 1 # 0 ==> Use Primal, 1==> Use Dual

f = Data.f            # facility opening costs (j)
c = Data.c            # transportation costs (i,j)
Lambda = Data.Lambda  # penalty costs (j)
u = Data.u            # facility capacities (i)
d = Data.d            # demands (s,j)

nS = len(d)   # the number of scenarios
p = [1.0/nS] * nS         # scenario probabilities (assuming equally likely scenarios)

# Build sets
I = range(len(c))
J = range(len(Lambda))
S = range(nS)

def ModifyAndSolveSP(s):
    # Modify constraint rhs
    for i in I:
        CapacityConsts[i].rhs = u[i] * xsol[i]
    for j in J:
        DemandConsts[j].rhs = d[s][j]
        SP.update()

    # Solve and get the DUAL solution
    SP.optimize()

    pi_sol = [DemandConsts[j].Pi for j in J]
    gamma_sol = [CapacityConsts[i].Pi for i in I]

    SPobj = SP.objVal

    print("Subproblem " + str(s))
    print('SPobj: %g' % SPobj)
    print("pi_sol: " + str(pi_sol))
    print("gamma_sol: " + str(gamma_sol))

    # Check whether a violated Benders cut is found
    CutFound = False
    if(nsol[s] < SPobj - CutViolationTolerance): # Found Benders cut is violated at the current master solution
        CutFound = True

    return SPobj, CutFound, pi_sol, gamma_sol

def ModifyAndSolveDSP(s):
    # Modify objective
    for i in I:
        gamma[i].obj = u[i] * xsol[i]
    for j in J:
        pi[j].obj = d[s][j]

    DSP.update()

    # Solve and get the solution
    DSP.optimize()

    pi_sol = [pi[j].x for j in J]
    gamma_sol = [gamma[i].x for i in I]

    DSPobj = DSP.objVal

    print("Subproblem " + str(s))
    print('DSPobj: %g' % DSPobj)
    print("pi_sol: " + str(pi_sol))
    print("gamma_sol: " + str(gamma_sol))

    # Check whether a violated Benders cut is found
    CutFound = False
    if(nsol[s] < DSPobj - CutViolationTolerance): # Found Benders cut is violated at the current master solution
        CutFound = True

    return DSPobj, CutFound, pi_sol, gamma_sol

##### Build the master problem #####
MP = Model("MP")
MP.Params.outputFlag = 0  # turn off output
MP.Params.method = 1      # dual simplex

# First-stage variables: facility openining decisions
x = MP.addVars(I, vtype=GRB.BINARY, obj=f, name='x')
n = MP.addVars(S, obj=p, name='n')
# Note: Default variable bounds are LB = 0 and UB = infinity

MP.modelSense = GRB.MINIMIZE

##### Build the subproblem(s) #####
if OptionForSubproblem == 0:
    # Build Primal SP
    SP = Model("SP")
    y = SP.addVars(I, J, obj=c, name='y')
    z = SP.addVars(J, obj=Lambda, name='z')

    DemandConsts = []
    CapacityConsts = []
    # Demand constraints
    for j in J:
        DemandConsts.append(SP.addConstr((y.sum('*',j) + z[j] == 0), "Demand"+str(j)))
    # Production constraints
    for i in I:
        CapacityConsts.append(SP.addConstr((y.sum(i,'*') <= 0), "Capacity" + str(i)))
    # NOTE: We will set the rhs of the constraints inside the loop later, so for now initialize them using your favorite number!

    SP.modelSense = GRB.MINIMIZE
    SP.Params.outputFlag = 0

else:
    # Build Dual SP
    DSP = Model("DSP")
    pi = DSP.addVars(J, ub=Lambda, obj=d[1], name='pi')
    gamma = []  # defined as non-positive variables
    for i in I:
        gamma.append(DSP.addVar(lb = -GRB.INFINITY, ub = 0, obj=u[i], name="gamma"+str(i)))

    DSP.addConstrs((pi[j] + gamma[i] <= c[i][j] for i in I for j in J), name='For_y')
    # Note: Dual constraints corresponding to z variables are just UBs on pi vars

    DSP.modelSense = GRB.MAXIMIZE
    DSP.Params.outputFlag = 0

##### Benders Loop #####
CutFound = True
NoIters = 0
BestUB = GRB.INFINITY
while(CutFound):
    NoIters += 1
    CutFound = False

    # Solve MP
    MP.update()
    MP.optimize()

    # Get MP solution
    MPobj = MP.objVal
    print('MPobj: %g' % MPobj)

    xsol = [0 for i in I]
    for i in I:
        if x[i].x > 0.99:
            xsol[i] = 1

    nsol = [n[s].x for s in S]
    print("xsol: " + str(xsol))
    print("nsol: " + str(nsol))

    UB = np.dot(f,xsol)

    for s in S:
        if OptionForSubproblem == 0:
            Qvalue, CutFound_s, pi_sol, gamma_sol = ModifyAndSolveSP(s)
        else:
            Qvalue, CutFound_s, pi_sol, gamma_sol = ModifyAndSolveDSP(s)

        UB += p[s] * Qvalue

        if(CutFound_s):
            CutFound = True
            expr = LinExpr(n[s] - quicksum(d[s][j]*pi_sol[j] for j in J) - quicksum(u[i]*gamma_sol[i]*x[i] for i in I))
            MP.addConstr(expr >= 0)
            print("CUT: " + str(expr) + " >= 0")

    if(UB < BestUB):
        BestUB = UB
    print("UB: " + str(UB) + "\n")
    print("BestUB: " + str(BestUB) + "\n")

print('\nOptimal Solution:')
print('MPobj: %g' % MPobj)
print("xsol: " + str(xsol))
print("nsol: " + str(nsol))
print("NoIters: " + str(NoIters))
