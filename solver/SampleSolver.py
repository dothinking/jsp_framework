import time
from collections import defaultdict
from model.solver import JSSolver
from model.problem import JSProblem
from model.solution import JSSolution


class SampleSolver(JSSolver):

    def do_solve(self, problem:JSProblem):
        '''A sample solving process.
        The sequence of operations assigned to each machine is determined by job id.        
        '''
        solution = JSSolution(problem)

        # group operations by machine
        machine_chains = defaultdict(list)
        for op in solution.ops:
            machine_chains[op.source.machine].append(op)
        
        # sort by job id, then create chain accordingly
        def create_chain(ops:list):
            pre = None
            for op in ops:
                op.pre_machine_op = pre
                pre = op

        for machine, ops in machine_chains.items():
            ops.sort(key=lambda op: op.source.job.id)
            create_chain(ops)
            solution.evaluate()

            # update solution
            time.sleep(1)
            problem.update_solution(solution)