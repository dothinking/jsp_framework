import logging
from jsp_fwk import (JSProblem, JSSolution)
from jsp_fwk.solver.GoogleORCPSolver import GoogleORCPSolver

# logging
logging.basicConfig(
    level=logging.INFO, 
    format="[%(asctime)s] %(message)s",
    datefmt='%Y-%m-%d %H:%M:%S')

def print_intermediate_solution(solution:JSSolution):
    logging.info(f'Makespan: {solution.makespan}')


if __name__=='__main__':

    problem = JSProblem(benchmark='ft10')

    s = GoogleORCPSolver()
    s.solve(problem=problem, interval=2000, callback=print_intermediate_solution)