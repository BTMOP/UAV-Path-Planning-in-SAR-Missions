
import random
import math

from gen_visual import loadbar

    # SA class, accepts SA_constants and problem to solve
    # Calls "sol_init", "sol_gen(sol)", "sol_cost(sol)"

class SA:
    def __init__(self, prob, constants):
        self.constants = constants
        self.prob = prob

    def run(self):
        print("Running SA...")

        sol = self.prob.sol_init()
        (cost, cost_p, cost_d, cost_n) = self.prob.sol_cost(sol)
        
        T = self.constants["T_init"]
        i = 1
        N = 1

        i_max = self.constants["i_max"]
        T_final = self.constants["T_final"]
        decay_rate = self.constants["decay"]["rate"]

        print_load_size = 50
        print_i_size = i_max // (print_load_size * 10)
        if ( print_i_size == 0 ):
            print_i_size = 1

        if ( self.constants["decay"]["type"] == "linear" ):
            if ( i_max == "auto" ):
                i_max = math.ceil((T - T_final)/decay_rate)
            elif ( T_final == "auto" ):
                T_final = T - (i_max + 1) * decay_rate
            elif ( decay_rate == "auto" ):
                decay_rate = (T - T_final) / i_max
        else:
            if ( i_max == "auto" ):
                i_max = math.ceil(math.log((T_final/T), decay_rate))
            elif ( T_final == "auto" ):
                T_final = T * ( decay_rate ** (i_max + 1) ) 
            elif ( decay_rate == "auto" ):
                decay_rate = (T_final / T) ** (1 / i_max)

        sol_init = sol
        sol_best, cost_best = sol, cost
        costs, costs_p, costs_d, costs_n = [cost], [cost_p], [cost_d], [cost_n]
        p_values = []
        p_i = []
        T_values = [T]
        N_uav_values = [sol["uav_count"]]

        while ( i <= i_max and T > T_final ):
            sol_new = self.prob.sol_gen(sol)
            (cost_new, cost_p_new, cost_d_new, cost_n_new) = self.prob.sol_cost(sol_new)
            delta_cost = cost_new - cost
            
            if ( delta_cost < 0 ):
                sol, cost, cost_p, cost_d, cost_n = sol_new, cost_new, cost_p_new, cost_d_new, cost_n_new
            else:
                p = math.exp((-1*delta_cost)/T)
                p_i.append(i)
                p_values.append(p)
                if ( p > random.uniform(0, 1) ):
                    sol, cost, cost_p, cost_d, cost_n = sol_new, cost_new, cost_p_new, cost_d_new, cost_n_new

            costs.append(cost)
            costs_p.append(cost_p)
            costs_d.append(cost_d)
            costs_n.append(cost_n)
            if ( cost < cost_best ):
                sol_best, cost_best = sol, cost
            T_values.append(T)
            N_uav_values.append(sol["uav_count"])

            if ( N == self.constants["N"] ):
                if ( self.constants["decay"]["type"] == "linear" ):
                    T_new = self.constants["T_init"] - i * decay_rate
                else:
                    T_new = self.constants["T_init"] * ( decay_rate ** i )
                if ( T_new > 0 ):
                    T = T_new
                
                i += 1
                N = 1
            else:
                N += 1

            if ( i % print_i_size == 0 ):
                print(loadbar(print_load_size, i, i_max), end='\r')
        
        print(loadbar(print_load_size, 1, 1))
        
        return {
            "sol": {
                "init": sol_init,
                "last": sol,
                "best": sol_best
            },
            "cost": {
                "all": costs,
                "best": cost_best,
                "p": costs_p,
                "d": costs_d,
                "n": costs_n
            },
            "p": {
                "i" : p_i,
                "values" : p_values
            },
            "T": T_values,
            "N_uav": N_uav_values
        }
