"""
Functions for solving the BUAP MIP and its relaxation
The model can be edited so that similar models can be solved without having to rebuild the whole model.
"""
import pyomo.environ as pyo
from pyomo.opt import SolverStatus, TerminationCondition
import time
from utils import *
from pyomo.core.base.constraint import Constraint
import time


def cap_init(m, j):
    return m.users_and_facs_df.at[j, 'capacity'] * m.cap_factor.value

def exp_travelers_init(m, i, j):
    return m.users_and_facs_df.at[i, 'population'] * m.travel_dict[i][j]

def obj_expression(m):
    if m.define_u:
        return sum(m.cap[j] * (1 - m.u[j]) ** 2 for j in m.facs)
    else:
        return sum(m.cap[j] * (
            1 - (sum(m.exp_travelers[(i, j)] * m.x[(i, j)] for (i, j2) in m.travel_pairs if j2 == j)
                 / m.cap[j])) ** 2 for j in m.facs)
    
def define_utilization(m,j):
    return m.u[j] == sum(m.exp_travelers[(i, j)] * m.x[(i, j)] for (i, j2) in m.travel_pairs if j2 == j) / m.cap[j]

def utilization_cstr(m, j):
    if m.define_u:
        return m.u[j] <= m.y[j]
    else:
        return sum(m.exp_travelers[(i, j)] * m.x[(i, j)] for (i, j2) in m.travel_pairs if j2 == j) / m.cap[
        j] <= m.y[j]

def assign_to_one_cstr(m, i):
    eligible_js = [j for (i2, j) in m.travel_pairs if i2 == i]
    if not eligible_js:
        return Constraint.Skip
        
    expr = sum(m.x[i, j] for j in eligible_js)
    
    if m.strict_assign_to_one:
        return expr == 1
    return expr <= 1

def y_init(m,j):
    if j in m.open_facs:
        return 1
    else:
        return 0
    

def build_BUAP_model_editable(users_and_facs_df, travel_dict, users, facs,
                        cap_factor, cutoff, open_facs, cap_dict = None, continous = False, 
                        define_u = True, num_consider = -1):
    """
    Build the BUAP but make the open facilites editable in the future
    :param users_and_facs_df: dataframe of the user and facility related input data
    :param travel_dict: dictionary of the travel probabilities from each user to each facility
    :param users: list of the users used in the instance
    :param facs: list of the facilities used in the instance
    :param cap_factor: factor by which all capacities are scaled
    ::param cutoff: minimum preference required for facility user pair to be considered;
      only used if num_consider is -1
    :param continous: whether to solve this model continously
    :param open_facs: open facilities
    :param define_u: whether to explicitely define u
    :param num_consider: number of closest facilities to consider for a user out of the open facilities, 
      same as n_r in paper; setting this to -1 means we use a cutoff instead
    :return: the built model
    """
    print('Build BUAP model...')
    start = time.time()
    m = pyo.ConcreteModel()
    m.users_and_facs_df = users_and_facs_df
    m.travel_dict = travel_dict

    # declare sets, variables and parameters
    m.users = pyo.Set(initialize=users)
    m.facs = pyo.Set(initialize=facs)
    m.open_facs = pyo.Set(initialize=open_facs, ordered = False)
    m.closed_facs = pyo.Set(initialize = list(set(facs) - set(open_facs)), ordered = False)
    m.cutoff = pyo.Param(initialize=cutoff)
    m.num_consider = pyo.Param(initialize=num_consider)
    if num_consider == -1:
        m.travel_pairs = pyo.Set(initialize=[(i, j) for i in m.users for j in m.facs
                                         if m.travel_dict[i][j] > m.cutoff.value])
    else:
        travel_pairs = [(i, j) for i in m.users for j in sorted(m.open_facs, key=lambda j_1: travel_dict[i][j_1], reverse=True)[0:num_consider]]
        travel_pairs = list(set(travel_pairs))
        m.travel_pairs = pyo.Set(initialize=travel_pairs)
    if cap_dict == None:
        m.cap_factor = pyo.Param(initialize=cap_factor)
        m.cap = pyo.Param(m.facs, initialize=cap_init)
    else:
        m.cap_factor = pyo.Param(initialize=cap_dict[facs[0]]/m.users_and_facs_df.at[facs[0], 'capacity'] )
        m.cap = pyo.Param(m.facs, initialize=lambda m, j: cap_dict[j])
    m.exp_travelers = pyo.Param(m.travel_pairs, initialize=exp_travelers_init)
    m.strict_assign_to_one = pyo.Param(initialize=True)
    m.continous = pyo.Param(initialize=continous)
    m.define_u = pyo.Param(initialize=define_u)
    m.y = pyo.Param(m.facs, initialize=y_init, mutable = True)

    if m.continous:
        m.x = pyo.Var(m.travel_pairs, bounds=(0,1))
    else:
        m.x = pyo.Var(m.travel_pairs, within=pyo.Binary)

    # fix pairs of closed facilities to be zero
    for (i,j) in m.travel_pairs:
        if j in m.closed_facs:
            m.x[(i,j)].fix(0)

    if m.define_u:
        m.u = pyo.Var(m.facs, bounds=(0, 1))

    # constraints and objective
    if m.define_u:
        m.define_utilization = pyo.Constraint(m.facs, rule=define_utilization)
    if not m.define_u:
        m.utilization_cstr = pyo.Constraint(m.facs, rule=utilization_cstr)
    m.assign_to_one_cstr = pyo.Constraint(m.users, rule=assign_to_one_cstr)
    m.obj = pyo.Objective(rule=obj_expression, sense=pyo.minimize)
    print('setup complete in ', time.time() - start, 'seconds')

    return m


def change_open_facs(m, new_open_facs, new_closed_facs):
    """
    Edit the input model m with the adapted open and closed facilities
    :param m: model that needs editing, created with build_BUAP_model_editable
    :param new_open_facs: facilities to be added to being open
    :param new_closed_facs: facilities that need to be closed now
    :return: the edited model
    """
    m.open_facs.update(set(new_open_facs))
    for j in new_closed_facs:
        m.open_facs.remove(j)
    m.closed_facs.update(set(new_closed_facs))
    for j in new_open_facs:
        m.closed_facs.remove(j)
    # update y variables
    for j in new_open_facs:
        m.y[j] = 1
    for j in new_closed_facs:
        m.y[j] = 0

    # fix pairs of closed facilities to be zero
    for (i,j) in m.travel_pairs:
        if j in new_closed_facs:
            m.x[(i,j)].fix(0)

    # unfix the ones that are not closed anymore
    for (i,j) in m.travel_pairs:
        if j in new_open_facs:
            m.x[(i,j)].unfix()
    return m

def optimize_BUAP_model_editable(m, threads=1, tolerance=0.0,time_limit = 10000):
    """
    Solve the BUAP
    the objective value is the objective value of the full model
    :param m: the model to be optimized
    :param threads: number of threads
    :param tolerance: tolerance on the optimality of the solution
    :param print_sol: boolean indicating whether the solution should be printed
    :param log_file: name of the log file. If "None", no log file will be produced
    :param time_limit: how long the model is allowed to run for
    :return: boolean indicating whether the model is feasible; updated results dictionary
    """
    print('Optimize BUAP model...')
    opt = pyo.SolverFactory("gurobi")
    opt.options["threads"] = threads
    opt.options["MIPGap"] = tolerance
    opt.options["NodefileStart"] = 0.5
    opt.options["Time_limit"] = time_limit
    start_time = time.time()
    res = opt.solve(m, tee=True)
    end_time = time.time()

    if res.solver.termination_condition == TerminationCondition.infeasible or res.solver.termination_condition == TerminationCondition.infeasibleOrUnbounded:
        return False, {}

    # create dictionary for the results after postprocessing
    assignment = {}
    results_x = {i : {} for i in m.users}
    for (i,j) in m.travel_pairs:
        results_x[i][j] = round(min(m.x[(i,j)].value,1.0), 5)
    # assign each user to facility with highest x_i,j
    if m.continous:
        assignment =  {i : max(results_x[i], key=results_x[i].get) for i in m.users}
    else: 
        for i in m.users:
            for j in m.open_facs:
                if (i, j) in m.travel_pairs and m.x[(i, j)].value > 1e-4:
                    assignment[i] = j
    results = {"solution_details":
                {"assignment": assignment, "open_facs": list(m.open_facs), "objective_value": pyo.value(m.obj),
                    "x": results_x, "u": { j: m.u[j].value for j in m.facs },
                    "lower_bound": res['Problem'][0]['Lower bound'], "solving_time": end_time - start_time},
            "model_details":
                {"users": list(m.users), "facs": list(m.facs), "cap_factor": m.cap_factor.value,
                    "budget_factor": len(m.open_facs)/len(m.facs), "cutoff": m.cutoff.value,
                    "num_consider_relaxation": m.num_consider.value,"strict_assign_to_one": m.strict_assign_to_one.value, "tolerance": tolerance,
                    "time_limit": time_limit, "define_u": m.define_u.value}
            }
    return True, results

def solve_BUAP_model_editable(users_and_facs_df, travel_dict, users, facs,
                        cap_factor, cutoff, open_facs, cap_dict = None, continous = False, 
                        define_u = True, num_consider = -1, 
                        threads=1, tolerance=0.0,time_limit = 10000):
    """
    Build and solve the BUAP model
    :param users_and_facs_df: dataframe of the user and facility related input data
    :param travel_dict: dictionary of the travel probabilities from each user to each facility
    :param users: list of the users used in the instance
    :param facs: list of the facilities used in the instance
    :param cap_factor: factor by which all capacities are scaled
    ::param cutoff: minimum preference required for facility user pair to be considered;
      only used if num_consider is -1
    :param continous: whether to solve this model continously
    :param open_facs: open facilities
    :param define_u: whether to explicitely define u
    :param num_consider: number of closest facilities to consider for a user out of the open facilities, 
      same as n_r in paper; setting this to -1 means we use a cutoff instead
    :param threads: number of threads
    :param tolerance: tolerance on the optimality of the solution
    :param print_sol: boolean indicating whether the solution should be printed
    :param log_file: name of the log file. If "None", no log file will be produced
    :param time_limit: how long the model is allowed to run for
    :return: boolean indicating whether the model is feasible and results dictionary
    """
    m = build_BUAP_model_editable(users_and_facs_df, travel_dict, users, facs,
                        cap_factor, cutoff, open_facs, cap_dict, continous, define_u, num_consider)
    is_feasible, result = optimize_BUAP_model_editable(m, threads, tolerance, time_limit)
    return is_feasible, result
