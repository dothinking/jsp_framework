import time
from jsp_fwk import (JSProblem, JSSolution, JSSolver)


class UserSolver(JSSolver):

    def do_solve(self, problem:JSProblem):
        '''A sample solving process: the sequence of operations assigned to each machine 
        is determined by job id. Obviously, it's a feasible but far from optimal solution.
        '''
        # (1) Initialize an empty solution from problem
        solution = JSSolution(problem)
       
        # (2) Solve or optimize the solution, i.e. determine the start_time of 
        # OperationStep instances. Note to evaluate solution explicitly if disjunctive 
        # graph model. In this case, just sort operations by job id, then create chain 
        # accordingly
        def create_chain(machine, ops:list):
            pre = machine
            for op in ops:
                op.pre_machine_op = pre
                pre = op

        for machine, ops in solution.machine_ops.items():
            ops.sort(key=lambda op: op.source.job.id)
            create_chain(machine, ops)
            solution.evaluate()

            # (3) Update the solution for problem iteratively
            time.sleep(1)
            problem.update_solution(solution)


if __name__=='__main__':

    problem = JSProblem(benchmark='ft10')

    s = UserSolver()
    s.solve(problem=problem, interval=2000, \
        callback=lambda solution: print(f'makespan: {solution.makespan}'))