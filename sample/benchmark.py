import logging
from jsp_fwk import (JSProblem, JSSolution, BenchMark)
from jsp_fwk.solver import (GoogleORCPSolver, PriorityDispatchSolver)


def print_intermediate_solution(solution:JSSolution):
    logging.info(f'Makespan: {solution.makespan}')


if __name__=='__main__':

    # ----------------------------------------
    # create problem from benchmark
    # ----------------------------------------
    names = ['ft06', 'la01', 'ft10', 'swv01', 'la38', 'ta24', \
            'ta31', 'swv12', 'ta24', 'ta42', 'ta54', 'ta68', 'ta69', 'ta70']
    problems = [JSProblem(benchmark=name) for name in names]

    # ----------------------------------------
    # test built-in solver
    # ----------------------------------------
    solvers = []

    # googl or-tools
    s = GoogleORCPSolver(max_time=300)

    # priority dispatching
    rules = ['spt', 'lpt', 'sps', 'lps', 'stpt', 'ltpt', 'ect', 'lct', \
             'swt', 'lwt', 'ltwr', 'mtwr', 'est', 'lst', 'hh', 'ihh']
    for i in [0, -5, -2, -1]:
        rule = rules[i]
        solvers.append(PriorityDispatchSolver(rule=rule, name=rule.upper()))

    # solvers = [s1,s2]

    # ----------------------------------------
    # solve and result
    # ----------------------------------------
    benchmark = BenchMark(problems=problems, solvers=solvers, num_threads=6)
    benchmark.run(show_info=True)