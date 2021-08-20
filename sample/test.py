import logging
from jsp_fwk import (JSProblem, JSSolution)
from jsp_fwk.solver.ortools import GoogleORCPSolver
from jsp_fwk.solver.dispatching_rule import PriorityDispatchSolver

# logging
logging.basicConfig(
    level=logging.INFO, 
    format="[%(asctime)s] %(message)s",
    datefmt='%Y-%m-%d %H:%M:%S')

def print_intermediate_solution(solution:JSSolution):
    logging.info(f'Makespan: {solution.makespan}')


if __name__=='__main__':

    problem = JSProblem(benchmark='la33')

    # s = GoogleORCPSolver()

    # s = PriorityDispatchSolver(rule='spt')
    # s = PriorityDispatchSolver(rule='mopr')
    # s = PriorityDispatchSolver(rule='mwkr')
    s = PriorityDispatchSolver(rule='t')

    s.solve(problem=problem, interval=2000, callback=print_intermediate_solution)