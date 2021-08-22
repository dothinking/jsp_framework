import logging
from jsp_fwk import (JSProblem, JSSolution)
from jsp_fwk.solver import (GoogleORCPSolver, PriorityDispatchSolver, PriorityDispatchProSolver)

# logging
logging.basicConfig(
    level=logging.INFO, 
    format="[%(asctime)s] %(message)s",
    datefmt='%Y-%m-%d %H:%M:%S')

def print_intermediate_solution(solution:JSSolution):
    logging.info(f'Makespan: {solution.makespan}')


if __name__=='__main__':

    # ----------------------------------------
    # create problem from benchmark
    # ----------------------------------------
    names = ['ft06', 'la01', 'ft10', 'swv01', 'la38', \
            'swv05', 'swv12', 'ta31', 'ta42', 'ta54', 'ta70']
    problem = JSProblem(benchmark='ft10')

    # ----------------------------------------
    # test built-in solver
    # ----------------------------------------
    # googl or-tools
    s = GoogleORCPSolver()

    # priority dispatching
    # s = PriorityDispatchSolver(rule='spt')
    # s = PriorityDispatchSolver(rule='mopr')
    # s = PriorityDispatchSolver(rule='mwkr')
    # s = PriorityDispatchSolver(rule='t')

    # ----------------------------------------
    # solve and result
    # ----------------------------------------
    s.solve(problem=problem, interval=None, callback=print_intermediate_solution)
    s.wait()
    print('----------------------------------------')
    if s.status:
        print(f'Optimum: {problem.optimum}')
        print(f'Solution: {problem.solution.makespan}')
        print(f'Terminate successfully in {s.user_time} sec.')
    else:
        print(f'Solving process failed in {s.user_time} sec.')
        