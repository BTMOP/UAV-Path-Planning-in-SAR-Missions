
from matplotlib.pyplot import pause
import opt_sa, opt_ga, opt_aco, opt_ba
import gen_env
import gen_prob
import gen_visual
import enum

class MH(enum.Enum):
    SA = 0
    GA = 1
    ACO = 2
    BA = 3

    # 'grid_layout' governs the auto-creation of a grid

grid_layout = {
    "grid_type": gen_env.GridType.rectangular,
    "grid_data": [10, 10],
    "base_type": gen_env.BaseType.edge,
    "priority_type": gen_env.PriorityType.diagonal,
    "rand_threshold": {
        "grid": 0.6,                # Ratio of cells from rectangle (GridType.random only)
        "priority": 0.1,            # Ratio of priorities (1) from cells (PriorityType.random only)
        "base": 0.2                 # Ratio of bases to (len_x + len_y ) of the map (BaseType.random_single/multiple)
    }
}

env_constants = {
    "uav": {
        "max_dist": 30,             # Max Distance covered by any UAV with full battery
        "charge_time": 1,           # Charging time
        "speed": 1,                 # Constant Speed
        "max": 3                    # Max no. of UAVs
    }
}

env = gen_env.Environment(grid_layout, env_constants)

prob_constants = {
    "switch_per": 50,               # Number of switching in path, switches = len('path')/'switch_per'
    "weights": {                    # Cost weights
        "priority": 1,
        "distance": 1,
        "uav": 30
    },
    "rand_N_uav": {                 # Governs list to choose from random N_uav for 'sol_gen'
        "range": 1,                 # Range +/- to choose from (e.g. for N_uav_prev = 2, range = 1, list = [1, 2, 3])
        "repeat": 2,                # Repeat N_uav_prev by in list (e.g. for 'repeat' = 2, list = [1, 2, 2, 2, 3])
        "init": "rand"              # 'sol_init' initial N_uav
    }
}

prob = gen_prob.Problem(env, prob_constants)

SA_constants = {
    "T_init": 50,
    "T_final": 1,
    "i_max": 100000,
    "N": 1,
    "decay": {
        "type": "geometrical",
        "rate": "auto"
    }
}

GA_constants = {
    "p": {
        "e" : 0.1,
        "c" : "auto",
        "m" : 0.2
    },
    "gen_size": 500,
    "i_max": 500
}

ACO_constants = {
    "alpha": 2,
    "decay": 0.2,
    "Q": 1,
    "size": 10,
    "i_max": 200
}

BA_constants = {            # Bee Algorithm parameters
    "flower_patches": 20,
    "min_switch_per": 20,       # Max. switch per is the max. num. of cells
    "foragers": {               # Number of foragers (solutions) for each patch
        "elite": 5,             
        "best": 4,
        "normal": 3,
        "global": 1
    },
    "ratio": {                  # Ratios from the flower patches
        "local": {
            "elite": 0.2,
            "best": 0.3,
        },
        "global": 0.1
    },
    "i_max": 500,
    "shrink_rate": 0.01        # Linear Shrinking Rate
}

to_run = MH.BA

if (to_run == MH.SA):
    MH = opt_sa.SA(prob, SA_constants)
elif (to_run == MH.GA):
    MH = opt_ga.GA(prob, GA_constants)
elif (to_run == MH.ACO):
    MH = opt_aco.ACO(prob, ACO_constants)
elif (to_run == MH.BA):
    MH = opt_ba.BA(prob, BA_constants)

results = MH.run()
gen_visual.visualize(MH, results, geometry=1)
