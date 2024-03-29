'''MIP solver with pulp framework.'''
from collections import defaultdict
import pulp
from ..common.exception import JSPException
from ..model.solver import JSSolver
from ..model.problem import JSProblem
from ..model.solution import JSSolution


class PuLPSolver(JSSolver):
    '''MIP solver with pulp framework.'''

    SOLVER_DICT = {
        'CBC': pulp.PULP_CBC_CMD,      # default by pulp
        'SCIP': pulp.SCIP_CMD,         # install and set env path manually
        'GUROBI': pulp.GUROBI_CMD
    }

    def __init__(self,
                 name:str='pulp',
                 solver_name:str='CBC',
                 max_time:int=None,
                 msg:bool=False) -> None:
        '''Solve JSP with PuLP, which is an LP modeler written in python. PuLP can generate MPS
        or LP files and call GLPK, COIN CLP/CBC, CPLEX, and GUROBI to solve linear problems.

        Args:
            name (str, optional): JSP solver name.
            solver_name (str, optional): solver for MIP, 'CBC', 'SCIP', 'GUROBI' for now.
                Default to CBC.
            max_time (int, optional): Max solving time in seconds. Defaults to None, i.e. no limit.
            msg (bool, optional): show solver log or not. Default to False.
        '''
        super().__init__(name)
        self.__solver_name = solver_name
        self.__msg = msg
        self.__max_time = max_time


    def do_solve(self, problem:JSProblem):
        '''Solve JSP with PuLP and the default CBC solver.
        https://github.com/KevinLu43/JSP-by-using-Mathematical-Programming-in-Python/
        '''
        # Initialize an empty solution from problem
        solution = JSSolution(problem, direct_mode=True)

        # create model
        model, variables = self.__create_model(solution)

        # solver
        solver_cmd = self.SOLVER_DICT.get(self.__solver_name.upper(), pulp.PULP_CBC_CMD)
        solver = solver_cmd(msg=self.__msg, timeLimit=self.__max_time, keepFiles=True)
        model.solve(solver)
        if model.status!=pulp.LpStatusOptimal:
            raise JSPException('No feasible solution found.')

        # assign pulp solution back to JSPSolution
        for op, var in variables.items():
            op.update_start_time(var.varValue)
        self.update_solution(solution) # update solution


    def __create_model(self, solution:JSSolution):
        '''Create PuLP model: variables, constraints and objective.'''
        # create the model
        model = pulp.LpProblem(f"min_makespan-{id(self)}", pulp.LpMinimize)

        # create variables
        # (1) start time of each operation
        max_time = sum(op.source.duration for op in solution.ops) # upper bound of variables
        variables = pulp.LpVariable.dicts(name='start_time', \
                                        indexs=solution.ops, \
                                        lowBound=0, \
                                        upBound=max_time, \
                                        cat='Integer')

        # (2) binary variable, i.e., 0 or 1, indicating the sequence of every two operations
        # assigned in same machine
        machine_ops = defaultdict(list)
        for op in solution.ops:
            machine_ops[op.source.machine].append(op)

        combinations = []
        for ops in machine_ops.values():
            combinations.extend(pulp.combination(ops, 2))
        bin_vars =  pulp.LpVariable.dicts(name='binary_var', \
                                     indexs=combinations, \
                                     lowBound=0, \
                                     cat='Binary')

        # objective: makespan
        s_max = pulp.LpVariable(name='max_start_time', \
                                lowBound=0, \
                                upBound=max_time, \
                                cat='Integer')
        model += s_max

        # apply constraints:
        # (1) the max start time
        for job in solution.job_ops:
            last_op = job.tail_job_op
            model += (s_max-variables[last_op]) >= last_op.source.duration

        # (2) operation sequence inside a job
        pre = None
        for op in solution.ops:
            if pre and pre.source.job==op.source.job:
                model += (variables[op]-variables[pre]) >= pre.source.duration
            pre = op

        # (3) no overlap for operations assigned to same machine
        for op_a, op_b in combinations:
            model += variables[op_a]-variables[op_b] >= \
                                op_b.source.duration - max_time*(1-bin_vars[op_a, op_b])
            model += variables[op_b]-variables[op_a] >= \
                                op_a.source.duration - max_time*bin_vars[op_a, op_b]

        return model, variables
 