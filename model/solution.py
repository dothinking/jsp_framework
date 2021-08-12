'''Job-Shop Schedule Problem.
'''



class JSProblem:
    '''Base class for Job Shop Schedule Problem.
    '''

    def __init__(self, jobs:list=None, 
                        num_jobs:int=0, num_machines:int=0, 
                        benchmark:str=None, 
                        input_file:str=None) -> None:
        """Initialize problem by job list, or random problem with specified count of jobs 
        and machines, or just load data from benchmark/user-defined file.

        Args:
            jobs (list, optional): Job list to schedule. 
            num_jobs (int, optional): Initialize random problem by specified count of jobs. 
            num_machines (int, optional): Initialize random problem by specified count of machines. 
            benchmark (str, optional): Benchmark name to load associated data.
            input_file (str, optional): User defined data file path. 
        """        
        self.__operations = None


    def solve(self):
        pass


    def store(self, filename):
        pass
    

    def __load_jobs(self, filename:str) -> list:
        pass


    def __generate_random_jobs(self, num_jobs:int, num_machines:int) -> list:
        pass


    def __create_job_chain(self, jobs:list):
        pass


    



class JSSolution(JSProblem):
    
    
    def sort(self) -> list:
        pass

    def makespan(self) -> float:
        pass


    def is_feasible(self) -> bool:
        pass


    
