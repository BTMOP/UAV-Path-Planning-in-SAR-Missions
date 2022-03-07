
import random
from gen_visual import loadbar

class GA:
    def __init__(self, prob, constants):
        self.constants = constants
        self.prob = prob

        # Straightforward, initial, randomized gen.

    def gen_init(self, total):
        gen = []
        for i in range(total):
            gen.append(self.prob.sol_init())
        return gen

        # Interpreting the constant parameters of GA, and setuping the size of each pop. segment

    def size(self):
        size = {}
        if ( self.constants["p"]["e"] == "auto" ):
            size["c"] = int( self.constants["p"]["c"] * self.constants["gen_size"] )
            size["m"] = int( self.constants["p"]["m"] * self.constants["gen_size"] )

            size["e"] = self.constants["gen_size"] - ( size["m"] + size["c"] )
        elif ( self.constants["p"]["c"] == "auto" ):
            size["e"] = int( self.constants["p"]["e"] * self.constants["gen_size"] )
            size["m"] = int( self.constants["p"]["m"] * self.constants["gen_size"] )

            size["c"] = self.constants["gen_size"] - ( size["e"] + size["m"] )
        elif ( self.constants["p"]["m"] == "auto" ):
            size["e"] = int( self.constants["p"]["e"] * self.constants["gen_size"] )
            size["c"] = int( self.constants["p"]["c"] * self.constants["gen_size"] )

            size["m"] = self.constants["gen_size"] - ( size["e"] + size["c"] )
        else:
            size["e"] = int( self.constants["p"]["e"] * self.constants["gen_size"] )
            size["c"] = int( self.constants["p"]["c"] * self.constants["gen_size"] )
            size["m"] = int( self.constants["p"]["m"] * self.constants["gen_size"] )
        
        size["total"] = size["e"] + size["c"] + size["m"]

        return size

        # Yields an array of costs, of all the population in a generation

    def gen_cost(self, gen, size):
        costs = []
        for i in range(size["total"]):
            (cost, cost_p, cost_d, cost_n) = self.prob.sol_cost(gen[i]) 
            costs.append(cost)
        return costs

        # Generates the elites of a next generation, based on a prev. gen. and Fitness-Based Selection

    def gen_e(self, gen, size):
        return self.gen_sort(gen, size)[0:size["e"]]
    
        # Generates children based on Elite Parenting Criteria and David's Cross-Over Algorigthm

    def gen_c(self, gen, size):
        elites = gen[0:size["c"]]
        to_return = []
        i_elite1 = 0
        i_elite2 = 1
        count = 0
        while ( True ):
            elite1 = elites[i_elite1]
            elite2 = elites[i_elite2]
            children = self.prob.sol_cross(elite1, elite2)
            if ( count == size["c"] ):
                break
            elif ( count == size["c"] - 1 ):
                to_return.append(children[0])
                break
            else:
                to_return += children
            count += 2

            i_elite1 += 2
            i_elite2 += 2
            if (i_elite1 >= len(elites)):
                i_elite1 -= len(elites)
            if (i_elite2 >= len(elites)):
                i_elite2 -= len(elites)

        return to_return

        # Generates mutated solutions based on randomized selection from the population

    def gen_m(self, gen, size):
        random.shuffle(gen)
        mutates = []
        for i in range(size["m"]):
            mutates.append(self.prob.sol_gen(gen[i]))
        
        return mutates

        # Sorts a generation, ascendingly, in terms of best/lowest cost

    def gen_sort(self, gen, size):
        costs_sort, throw_away, gen_sort = zip(*sorted(zip(self.gen_cost(gen, size), range(size["total"]), gen)))   
        return gen_sort

        # Returns the best solution of a generation

    def gen_best(self, gen, size):
        return self.gen_sort(gen, size)[0]

        # Runs the conventional GA algorigthm

    def run(self):
        print("Running GA...")

        size = self.size()
        gen = self.gen_init(size["total"])
        i = 1

        print_load_size = 50
        print_i_size = self.constants["i_max"] // (print_load_size * 10)
        if ( print_i_size == 0 ):
            print_i_size = 1

        sol_init = self.gen_best(gen, size)
        (cost, cost_p, cost_d, cost_n) = self.prob.sol_cost(sol_init)
        costs, costs_p, costs_d, costs_n = [cost], [cost_p], [cost_d], [cost_n]
        
        while ( i <= self.constants["i_max"] ):
            gen_new = []
            gen_new += self.gen_e(gen, size)
            gen_new += self.gen_c(gen, size)
            gen_new += self.gen_m(gen, size)
            gen = gen_new

            sol = self.gen_best(gen, size)
            (cost, cost_p, cost_d, cost_n) = self.prob.sol_cost(sol)
            costs.append(cost)
            costs_p.append(cost_p)
            costs_d.append(cost_d)
            costs_n.append(cost_n)

            i += 1

            if ( i % print_i_size == 0 ):
                print(loadbar(print_load_size, i, self.constants["i_max"]), end='\r')
        print(loadbar(print_load_size, 1, 1))

        sol_best = self.gen_best(gen, size)
        (cost_best, cost_best_p, cost_best_d, cost_best_n) = self.prob.sol_cost(sol_best)

        return {
            "sol": {
                "init": sol_init,
                "best": sol_best
            },
            "cost": {
                "all": costs,
                "best": cost_best,
                "p": costs_p,
                "d": costs_d,
                "n": costs_n
            }
        }
