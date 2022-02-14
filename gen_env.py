
import enum
import random

    # The environment module, "gen_env", contains the Environment class, and enum types related to it.
    # Its function is to generate object that represent the external environment.
    # In addition, it allows to auto-generation of random environments of differing sizes and properties,
    #   to test on.

class BaseType(enum.Enum):      # Different types of base configurations to auto-generate
    corner = 0
    edge = 1
    single = 2
    random_single = 3
    random_multiple = 4

class PriorityType(enum.Enum):      # Different types of priority configurations to auto-generate
    none = 0
    diagonal = 1
    random = 2

class GridType(enum.Enum):        # Different types of grid configurations to auto-generate
    rectangular = 0
    random = 1

class Environment:

        # Accepts two dictionaries, 'grid_layout' and 'constants', governing the grid structure and constants related
        #   to the environment. Examples of both dictionaries in 'main' script

    def __init__(self, grid_layout, constants):
        self.constants = constants
        self.gen_grid(grid_layout)

        # Generate grid, based on 'grid_layout' options

    def gen_grid(self, grid_layout):
        self.cells = []                 # To contain all (x,y) cells of the grid
        self.priorities = []            # Corresponding priorities of each cell
        self.bases = []                 # (x,y) of bases along the outer bounds
        self.bounds = {
            "x" : [0, 0],
            "y" : [0, 0]
        }

        len_x, len_y = grid_layout["grid_data"][0], grid_layout["grid_data"][1]
        self.bounds["x"][1], self.bounds["y"][1] = len_x, len_y
        
        if (grid_layout["grid_type"] == GridType.rectangular):
            for y in range(len_y):
                for x in range(len_x):
                    self.cells.append([x+0.5, y+0.5])
        elif (grid_layout["grid_type"] == GridType.random):
            grid_threshold = 0.8
            if ( "rand_threshold" in grid_layout ):
                grid_threshold = grid_layout["rand_threshold"]["grid"]

            for y in range(len_y):
                for x in range(len_x):
                    if ( random.uniform(0, 1) <= grid_threshold ):
                        self.cells.append([x+0.5, y+0.5])

        self.gen_priorities(grid_layout)
        self.gen_bases(grid_layout)

        # Generate priorities, based on 'grid_layout' options
    
    def gen_priorities(self, grid_layout):
        if (grid_layout["priority_type"] == PriorityType.random):
            priority_threshold = 0.2
            if ( "rand_threshold" in grid_layout ):
                priority_threshold = grid_layout["rand_threshold"]["priority"]

            for cell in self.cells:
                if ( random.uniform(0, 1) <= priority_threshold ):
                    self.priorities.append(1)
                else:
                    self.priorities.append(0) 
        elif (grid_layout["priority_type"] == PriorityType.diagonal):
            for cell in self.cells:
                if ( cell[0] == cell[1] or cell[0] == -1*cell[1]):
                    self.priorities.append(1)
                else:
                    self.priorities.append(0)
        else:
            for cell in self.cells:
                self.priorities.append(0)  

        # Generate bases, based on 'grid_layout' options
        
    def gen_bases(self, grid_layout):
        len_x, len_y = grid_layout["grid_data"][0], grid_layout["grid_data"][1]

        if (grid_layout["base_type"] == BaseType.edge):
            self.bases.append([len_x/2, -0.5])
            self.bases.append([-0.5, len_y/2])
            self.bases.append([len_x/2, len_y+0.5])
            self.bases.append([len_x+0.5, len_y/2])
        elif (grid_layout["base_type"] == BaseType.corner):
            self.bases.append([-0.5, -0.5])
            self.bases.append([-0.5, len_y+0.5])
            self.bases.append([len_x+0.5, len_y+0.5])
            self.bases.append([len_x+0.5, -0.5])
        elif (grid_layout["base_type"] == BaseType.single):
            self.bases.append([len_x/2, len_y+0.5])
        elif (grid_layout["base_type"] == BaseType.random_single or grid_layout["base_type"] == BaseType.random_multiple):
            bases_set = []
            for i in range(len_x):
                bases_set.append([i+0.5, -0.5])
                bases_set.append([i+0.5, len_y+0.5])
            for i in range(len_y):
                bases_set.append([-0.5, i+0.5])
                bases_set.append([len_x+0.5, i+0.5])

            if ( grid_layout["base_type"] == BaseType.random_single ):
                self.bases.append( bases_set[random.randrange(0, len(bases_set))] )
            elif ( grid_layout["base_type"] == BaseType.random_multiple ):
                num_bases = int((len_y + len_x)*0.3)
                if ( "rand_threshold" in grid_layout ):
                    num_bases = int( (len_y + len_x) * grid_layout["rand_threshold"]["base"] )
                added = []
                i = 0
                while ( i < num_bases ):
                    i_r = random.randrange(0, len(bases_set))
                    if ( i_r not in added ):
                        added.append(i_r)
                        self.bases.append(bases_set[i_r])
                        i += 1
