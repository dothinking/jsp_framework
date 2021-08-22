import threading
from queue import Queue
from jsp_fwk import JSProblem
from jsp_fwk.solver import GoogleORCPSolver


# solving
def solve(names_queue:Queue, res, thread_name:str):
    while True:
        name = names_queue.get()
        p = JSProblem(benchmark=name)
        s = GoogleORCPSolver(max_time=600) # set upper limit of solving time
        s.solve(problem=p, interval=None)
        s.wait() # wait for termination

        # collect results
        optimum = p.optimum
        cal_value = p.solution.makespan
        ref = (optimum[0]+optimum[1])/2 if isinstance(optimum, tuple) else optimum
        items = [name, len(p.jobs), len(p.machines), optimum, \
                    cal_value, round((cal_value/ref-1)*100,1), s.user_time]
        res.append(','.join(map(str, items)))

        names_queue.task_done()
        print(f'{thread_name} processed {name}.')


if __name__=='__main__':

    # benchmarks
    names = ['ft06', 'la01', 'ft10', 'swv01', 'la38', \
            'ta31', 'swv12', 'ta42', 'ta54', 'ta70']
    names_queue = Queue(maxsize=20)
    for name in names: names_queue.put(name)
    
    # result
    res = []
    res.append('name,num_job,num_machine,optimum,solution,time')

    # create child threads
    for i in range(4):
        thread = threading.Thread(target=solve, args=(names_queue, res, f'Child-{i}'))
        thread.setDaemon(True)
        thread.start()

    # wait for termination
    names_queue.join()

    # final results
    print()
    for line in res: print(line)