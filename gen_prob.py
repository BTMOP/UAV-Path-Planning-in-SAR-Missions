
import random
import copy
from gen_visual import plot_path
from util import cum_sel

    # The Problem class, governs everything related to our problem, and its solution generation/cost function.
    # It accepts the environment, and some problem-specific constants. An example of the constants is in the 'main' script.

    # sol_init, sol_gen(sol), sol_cost(sol), sol_cross(sol1, sol2) are the functions for algorigthms to call.

    # 'sol' is a dictionary, containing a path as an array of indexes of all grid cells, in an ordered fashion. (path)
    # These paths are further divided equally among the number of UAVs. (path_uavs)
    # Each path for each UAV is converted into subpaths. (divisions)
    # For each division, there're (ranges), (distances), and (bases)
    # (ranges) is an array, containing ranges of indexes in (path_uav), e.g. [start, end], which denote
    #       the path of the uav between every land and launch
    # (bases) denote the launch and landing bases for every range
    # (distance) denotes distance covered per flight

class Problem:
    def __init__(self, env, constants):
        self.env = env
        self.constants = constants

        # Generates an initial, feasible solution
        # A path contains indexes of all (x, y) grid cells, in an ordered, randomized fashion.
        # This path is chosen naively, with a random/max number of UAVs.
        # These two parameters are passed to 'get_sol_from_path' to generate a solution.

    def sol_init(self):
        path = list(range(len(self.env.cells)))
        random.shuffle(path)
        if ( self.constants["rand_N_uav"]["init"] == "max" ):
            N_uav = self.env.constants["uav"]["max"]
        else:
            N_uav = random.randrange(1, self.env.constants["uav"]["max"]+1)
        return self.get_sol_from_path(path, N_uav)

        # Straightforward cost calculation, with exception of 'priority_cost', explained later
    
    def sol_cost(self, sol):
        cost_p = self.constants["weights"]["priority"] * self.priority_cost_multi(sol)
        cost_d = self.constants["weights"]["distance"] * sol["divisions"]["total"]
        cost_n = self.constants["weights"]["uav"] * sol["uav_count"]
        cost = cost_p + cost_d + cost_n
        return (cost, cost_p, cost_d, cost_n)

        # The generation of a new solution involves randomizing two parameters:
        # Number of UAVs, 'path' array
        # Thereafter, these are run by the function 'get_sol_from_path'.

    def sol_cost_quick(self, sol):
        return self.sol_cost(sol)[0]

        # Generating a new solution, based on a previous one.

    def sol_gen(self, sol):
        return self.sol_gen_custom(sol, self.constants["switch_per"])

    def sol_gen_custom(self, sol, switch_per):
        path_copy = copy.copy(sol["path"])
        path_len = len(sol["path"])
        switch_times = path_len//switch_per
        for x in range(switch_times):
            i1 = random.randrange(0, path_len)
            i2 = random.randrange(0, path_len)
            path_copy[i1], path_copy[i2] = path_copy[i2], path_copy[i1]

        N_uav_new = self.rand_N_uav(sol["uav_count"])

        return self.get_sol_from_path(path_copy, N_uav_new)

        # Uses David's crossover criteria to mate two parent solutions
        # Utilizes an arithmetic randomized selection of the N_uav value

    def sol_cross(self, sol1, sol2):
        len_path = len(sol1["path"])
        i_cut = random.randrange(1, len_path)
        path1 = sol1["path"][0:i_cut]
        path2 = sol2["path"][0:i_cut]
        i = i_cut
        i_count = 0
        while ( i_count < len_path ):
            if ( sol1["path"][i] not in path2 ):
                path2.append(sol1["path"][i])
            if ( sol2["path"][i] not in path1 ):
                path1.append(sol2["path"][i])

            i += 1
            if ( i == len_path ):
                i = 0
            i_count += 1
        
        N_uav_max = max(sol1["uav_count"], sol2["uav_count"])
        N_uav_min = min(sol1["uav_count"], sol2["uav_count"])
        N_uav = random.randrange(N_uav_min, N_uav_max+1)

        return [
            self.get_sol_from_path(path1, N_uav),
            self.get_sol_from_path(path2, N_uav)
        ]
    
    def sol_ant(self, phermone, phermone_N, alpha):

            # Generating Path

        bucket = list(range(len(self.env.cells)))
        path = [random.choice(bucket)]
        bucket.remove(path[0])
        while (len(bucket) != 0):
            pher_arr = [0] * len(bucket)
            for j in range(len(bucket)):
                curr_pher = phermone.access(path[-1], bucket[j]) ** alpha
                pher_arr[j] = curr_pher
            sum_pher = sum(pher_arr)
            probab_arr = [pher/sum_pher for pher in pher_arr]

            next_cell = bucket[cum_sel(probab_arr)]
            path += [next_cell]
            bucket.remove(next_cell)

            # Generating N
        
        sum_pher_N = sum(phermone_N)
        probab_N_arr = [pher_N/sum_pher_N for pher_N in phermone_N]
        N = 1 + cum_sel(probab_N_arr)

        return self.get_sol_from_path(path, N)

    def access_phermone(self, phermone, i, j):
        if (i > j):
            i, j = j, i
        # print(str(i) + ", " + str(j) + " -> " + str(i) + ", " + str(j-1-i))
        return phermone[i][j-1-i]

        # Utilized by 'sol_gen' to randomize the number of UAVs selection process
        # Creates a list of possible N_uav values, and randomizes the selection, while checking feasibility.

    def rand_N_uav(self, N_uav):
        rand_list_repeat = [N_uav] * self.constants["rand_N_uav"]["repeat"]
        rand_list_range_over = list(range(N_uav+1, N_uav+1+self.constants["rand_N_uav"]["range"]))
        rand_list_range_under = list(range(N_uav-self.constants["rand_N_uav"]["range"], N_uav))
        rand_list = rand_list_range_over + rand_list_range_under + rand_list_repeat
        
        N_uav_new = random.choice(rand_list)
        if (N_uav_new < 1):
            N_uav_new = 1
        elif (N_uav_new > self.env.constants["uav"]["max"]):
            N_uav_new = self.env.constants["uav"]["max"]
        
        return N_uav_new

        # Divides a 'path' into 'path_uavs', then further into sub-paths, to return a feasible solution.

    def get_sol_from_path(self, path, N_uav):
        path_uavs = self.divide_path_multi(path, N_uav)
        divisions = []
        total = 0
        for path_uav in path_uavs:
            division = self.divide_path(path_uav)
            divisions.append(division)
            total += division["total"]

        sol = {
            "path": path,
            "path_uavs": path_uavs,
            "uav_count": len(path_uavs),
            "divisions": {
                "content" : divisions,
                "total" : total
            }
        }

        return sol

        # Runs a loop across all divisions to calculate the priority cost of each UAV.

    def priority_cost_multi(self, sol):
        cost = 0
        for i in range(sol["uav_count"]):
            division = sol["divisions"]["content"][i]
            path = sol["path_uavs"][i]
            cost += self.priority_cost(path, division["ranges"], division["bases"])
        return cost

        # Calculates the priority cost for a single UAV path, and its subpaths.
        # Estimates the time passed before reaching a grid cell, taking into account:
        #   No. of times having to charge (assuming full-charge), distance to location (assuming constant speed)

    def priority_cost(self, path, ranges, bases):
        cost_p_dist, cost_p_charge = 0, 0
        dist = 0
        charge_count = 0
        for iDiv in range(len(ranges)):
            first_i = path[ranges[iDiv][0]]
            dist += self.calc_dist(self.env.bases[bases[iDiv][0]], self.env.cells[first_i])
            for iCell in range(ranges[iDiv][0], ranges[iDiv][1] + 1):
                if (iCell != ranges[iDiv][0]):
                    midA_i = path[iCell - 1]
                    midB_i = path[iCell]
                    dist += self.calc_dist(self.env.cells[midA_i], self.env.cells[midB_i])
                cell_i = path[iCell]
                cost_p_dist += dist * self.env.priorities[cell_i]
                cost_p_charge += charge_count * self.env.priorities[cell_i]
            last_i = path[ranges[iDiv][-1]]
            dist += self.calc_dist(self.env.bases[bases[iDiv][1]], self.env.cells[last_i])
            charge_count += 1

        cost_p_dist = cost_p_dist / self.env.constants["uav"]["speed"]
        cost_p_charge = cost_p_charge * self.env.constants["uav"]["charge_time"]

        return cost_p_dist + cost_p_charge

        # Divides a 'path' into an array of paths, 'path_uavs', by calculating an average middle distance between all cells,
        #   and dividing the cells into chunks.

    def divide_path_multi(self, path, N_uav):
        dist_div = ( self.calc_dist_cells(path, 0, len(path)-1) / (len(path)-1) ) * ( (len(path)-N_uav) / N_uav )
        iStart, iEnd = 0, 0
        ranges_uav = []
        while (True):
            if ( len(ranges_uav) == (N_uav-1) ):
                ranges_uav.append([iStart, len(path)-1])
                break

            if (iEnd == len(path)):
                if (iStart != iEnd):
                    ranges_uav.append([iStart, len(path)-1])
                break

            dist = self.calc_dist_cells(path, iStart, iEnd)
            if (dist >= dist_div):
                ranges_uav.append([iStart, iEnd])
                iEnd += 1
                iStart = iEnd
            else:
                iEnd += 1
        
        path_uav = []
        for range_uav in ranges_uav:
            path_uav.append(path[range_uav[0]:(range_uav[1]+1)])
        
        return path_uav

        # Divides a specific-uav path into subpaths

    def divide_path(self, path):
        iStart, iEnd, dist_sum_prev, dist_total = 0, 0, 0, 0
        divisions = []
        dist_divisions = []
        bases = []
        launch = random.randrange(0, len(self.env.bases))
        land = random.randrange(0, len(self.env.bases))
        bases.append([launch, land])

        while (iEnd < len(path)):
            dist_base_from = self.calc_dist(self.env.bases[launch], self.env.cells[path[iStart]])
            dist_base_to = self.calc_dist(self.env.bases[land], self.env.cells[path[iEnd]])
            dist_between = self.calc_dist_cells(path, iStart, iEnd)
            dist_sum_curr = dist_base_from + dist_base_to + dist_between

            if (dist_sum_curr <= self.env.constants["uav"]["max_dist"]):
                dist_sum_prev = dist_sum_curr
                iEnd += 1
            else:
                divisions.append([iStart, iEnd-1])
                dist_divisions.append(dist_sum_prev)
                dist_total += dist_sum_prev
                bases.append([launch, land])

                iStart = iEnd
                launch = land
                land = random.randrange(0, len(self.env.bases))
        
        divisions.append([iStart, iEnd-1])
        dist_divisions.append(dist_sum_prev)
        dist_total += dist_sum_prev
        bases.append([launch, land])

        return {
            "ranges": divisions,
            "distances": dist_divisions,
            "total": dist_total,
            "bases": bases
        }

        # Calculates distance between a number of cells

    def calc_dist_cells(self, path, iStart, iEnd):
        dist = 0
        while (iStart != iEnd):
            dist += self.calc_dist(self.env.cells[path[iStart]], self.env.cells[path[iStart+1]])
            iStart += 1
        return dist

        # Calculates distance between two (x, y)'s

    def calc_dist(self, pt1, pt2):
        return ( (pt1[0]-pt2[0])**2 + (pt1[1]-pt2[1])**2 )**(1/2)        

