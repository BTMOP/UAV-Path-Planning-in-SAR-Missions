
import random
import sys

from numpy.core.numeric import convolve
from gen_visual import loadbar

class Phermone:
    def __init__(self, size, val=1.0):
        self.content = [None] * (size - 1)
        for i in range(size-1):
            sub_phermone = [val] * (size-i-1)
            self.content[i] = sub_phermone

    def access(self, i, j):
        i, j = self.convert(i, j)
        return self.content[i][j]

    def convert(self, i, j):
        if (i > j):
            i, j = j, i
        # print(str(i) + ", " + str(j) + " -> " + str(i) + ", " + str(j-1-i))
        return i, j-1-i

    def evaporate(self, decay):
        for j in range(len(self.content)):
            for k in range(len(self.content[j])):
                self.content[j][k] *= 1 - decay
    
    def update(self, i, j, val):
        i, j = self.convert(i, j)
        self.content[i][j] += val

class ACO:
    def __init__(self, prob, constants):
        self.constants = constants
        self.prob = prob

        # Returns the best solution of a generation

    def best_ant(self, colony):
        best_cost = sys.float_info.max
        return_ant = None
        for ant in colony:
            (cost, cost_p, cost_d, cost_n) = self.prob.sol_cost(ant)
            if (cost <= best_cost):
                return_ant = ant
                best_cost = cost

        return (return_ant, best_cost)

    def run(self):
        print("Running ACO...")

        print_load_size = 50
        print_i_size = self.constants["i_max"] // (print_load_size * 10)
        if ( print_i_size == 0 ):
            print_i_size = 1

        phermone = Phermone(len(self.prob.env.cells))
        phermone_N = [1] * self.prob.env.constants["uav"]["max"]
    
        i = 1
        costs, costs_p, costs_d, costs_n = [], [], [], []

        top_ant = self.prob.sol_init()
        top_cost = self.prob.sol_cost(top_ant)[0]
        init_ant = top_ant

        while ( i <= self.constants["i_max"] ):

                # Colony Generation

            colony = []
            for j in range(self.constants["size"]):
                colony += [self.prob.sol_ant(phermone, phermone_N, self.constants["alpha"])]

            best_ant, best_cost = self.best_ant(colony)

            if ( best_cost <= top_cost ):
                top_cost = best_cost
                top_ant = best_ant

            (cost, cost_p, cost_d, cost_n) = self.prob.sol_cost(best_ant)
            costs.append(cost)
            costs_p.append(cost_p)
            costs_d.append(cost_d)
            costs_n.append(cost_n)

                # Phermone Evaporation
            
            phermone.evaporate(self.constants["decay"])
        
            for j in range(len(phermone_N)):
                phermone_N[j] *= 1 - self.constants["decay"]

                # Phermone Deposition

            for ant in colony:
                cost = self.prob.sol_cost(ant)[0]
                to_add = self.constants["Q"]*(1/cost)
                for j in range(len(ant["path"])-1):
                    phermone.update(ant["path"][j], ant["path"][j+1], to_add)
                phermone_N[ant["uav_count"]-1] += to_add

            i += 1

            if ( i % print_i_size == 0 ):
                print(loadbar(print_load_size, i, self.constants["i_max"]), end='\r')
        print(loadbar(print_load_size, 1, 1))

        return {
            "sol": {
                "init": init_ant,
                "best": top_ant
            },
            "cost": {
                "all": costs,
                "best": top_cost,
                "p": costs_p,
                "d": costs_d,
                "n": costs_n
            }
        }
