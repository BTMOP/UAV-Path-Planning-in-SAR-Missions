
import random, math
from types import new_class
from gen_visual import loadbar

class Flowers:
    def __init__(self, BA):
        self.BA = BA
        self.constructor()

    def constructor(self):
            # Determining sizes
        self.size = { "all": self.BA.constants["flower_patches"] }

        self.size["global"] = math.floor(self.BA.constants["ratio"]["global"] * self.size["all"])
        self.size["local"] = self.size["all"] - self.size["global"]

        self.size["best"] = math.floor(self.BA.constants["ratio"]["local"]["best"] * self.size["all"])
        self.size["elite"] = math.floor(self.BA.constants["ratio"]["local"]["elite"] * self.size["all"])
        self.size["normal"] = self.size["local"] - self.size["best"] - self.size["elite"]

            # Random local-search scouts initialized
        self.scouts = []
        for i in range(self.size["local"]):
            self.scouts.append(self.BA.prob.sol_init())

            # Creating the neighbourhoods size variable
        self.neighbourhoods = [0] * self.size["local"]

            # Get access ranges for elite, best, normal
        self.foragers = [self.BA.constants["foragers"]["elite"]] * self.size["elite"]
        self.foragers += [self.BA.constants["foragers"]["best"]] * self.size["best"]
        self.foragers += [self.BA.constants["foragers"]["normal"]] * self.size["normal"]

            # Get initial costs, indexes
        self.costs = self.cost_scouts(self.scouts)
        self.indexes = self.sort_scouts(self.costs)

            # Random global-search scouts (explorers) initialized
        self.size["explorers"] = self.size["global"]*self.BA.constants["foragers"]["global"]
        self.explorers = []
        for i in range(self.size["explorers"]):
            self.explorers.append(self.BA.prob.sol_init())

            # Order the explorers
        self.order_explorers()

    def search(self):
            # Local search
        for i in range(self.size["local"]):
            switch_per = self.get_switch_per(self.neighbourhoods[self.indexes[i]])
            new_scout = None
            for j in range(self.BA.constants["foragers"]["elite"]):
                potential = self.BA.prob.sol_gen_custom(self.scouts[self.indexes[i]], switch_per)
                cost = self.BA.prob.sol_cost_quick(potential)
                if ( cost < self.costs[self.indexes[i]] ):
                    new_scout, new_cost = potential, cost
            if ( new_scout != None ):
                self.scouts[self.indexes[i]] = new_scout
            else:
                self.neighbourhoods[self.indexes[i]] += 1
                if ( self.neighbourhoods[self.indexes[i]] > len(self.BA.prob.env.cells) ):
                    self.scouts[self.indexes[i]] = self.new_scout()
                    self.neighbourhoods[self.indexes[i]] = 0
        
            # Reset costs, indexes
        self.costs = self.cost_scouts(self.scouts)
        self.indexes = self.sort_scouts(self.costs)

    def explore(self):
            # Global Search
        for i in range(self.size["explorers"]):
            self.explorers.append(self.BA.prob.sol_init())

            # Re-order double the explorers, then cut in half
        self.order_explorers()
        self.explorers = self.explorers[0:self.size["explorers"]]

    def order_explorers(self):
        costs_sort, throw_away, sorted_explorers = zip(*sorted(zip(self.cost_scouts(self.explorers), range(self.size["explorers"]), self.explorers)))
        self.explorers = list(sorted_explorers)

        # New local search scout, selected from explorers or randomized
    def new_scout(self):
        to_return = None
        if (len(self.explorers) > 0):
            to_return = self.explorers[0]
            del self.explorers[0]
        else:
            to_return = self.BA.prob.sol_init()
        return to_return

        # Switch_Per is the method by which we control the size of a scout's neighbourhood
        # By switching cells a lower number of times in a given solution, the neighbourhood from a scout is essentially smaller
    def get_switch_per(self, neighbourhood):
        x = len(self.BA.prob.env.cells) - self.BA.constants["min_switch_per"]
        y = neighbourhood * self.BA.constants["shrink_rate"]
        z = math.ceil(x * y + self.BA.constants["min_switch_per"])
        return z

    def cost_scouts(self, scouts):
        costs = []
        for scout in scouts:
            costs.append(self.BA.prob.sol_cost_quick(scout))
        return costs

    def cost_patches(self, patches):
        costs = []
        for patch in patches:
            costs.append(self.cost_scouts(patch))
        return costs
        
    def sort_scouts(self, costs):
        ignore, indexes = zip(*sorted(zip(costs, range(len(costs)))))
        return indexes

class BA:
    def __init__(self, prob, constants):
        self.constants = constants
        self.prob = prob

    def run(self):
        print("Running BA...")

        flowers = Flowers(self)
        sol_init = flowers.scouts[flowers.indexes[0]]

        (cost, cost_p, cost_d, cost_n) = self.prob.sol_cost(sol_init)
        costs, costs_p, costs_d, costs_n = [cost], [cost_p], [cost_d], [cost_n]

        sol_best = sol_init
        cost_best = cost

            # Loading bar ...
        print_load_size = 50
        print_i_size = self.constants["i_max"] // (print_load_size * 10)
        if ( print_i_size == 0 ):
            print_i_size = 1

        for i in range(self.constants["i_max"]):
            flowers.search()
            flowers.explore()

                # If local-best is best
            if ( flowers.costs[flowers.indexes[0]] < cost_best ):
                cost_best = flowers.costs[flowers.indexes[0]]
                sol_best = flowers.scouts[flowers.indexes[0]]

                # If global-best is best
            cost_explore = self.prob.sol_cost_quick(flowers.explorers[0])
            if ( cost_explore < cost_best ):
                cost_best = cost_explore
                sol_best = flowers.explorers[0]
 
            (cost, cost_p, cost_d, cost_n) = self.prob.sol_cost(flowers.scouts[flowers.indexes[0]])
            costs.append(cost)
            costs_p.append(cost_p)
            costs_d.append(cost_d)
            costs_n.append(cost_n)

            if ( i % print_i_size == 0 ):
                print(loadbar(print_load_size, i, self.constants["i_max"]), end='\r')
        print(loadbar(print_load_size, 1, 1))

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
