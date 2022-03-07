
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as matcolor
import matplotlib as mat
import math

    # This module is responsible for visualizing the results obtained from any algorithm.
    # It contains 'matplotlib' specific functions.

    # NOTE: In geometry, different colors represent different UAVs
    # Dark dots represent high priority cells
    # Grey dots represent low priority cells
    # Dark square(s) represent base(s)

constants = {
    "grid_major_step": 5,
    "grid_minor_step": 1,
    "colors": {
        "path": [
            [0.25, 0.5, 0.74, 0.5],
            [0.3, 0.74, 0.25, 0.5],
            [0.55, 0.25, 0.74, 0.5],
            [0.74, 0.25, 0.25, 0.5],
            [0.274, 0.61, 0.25, 0.5]
        ],
        "cell_hi": [0, 0, 0, 0.7],
        "cell_lo": [0, 0, 0, 0.2],
        "base": [0, 0, 0, 1],
        "title": [0, 0, 0, 0.5]
    },
    "markers": {
        "cell_hi": "o",
        "cell_lo": "o",
        "base": "s",
        "p" : "x"
    },
    "timestep": {
        "subpath": 1.5,
        "analytical": 1.5
    },
    "title": {
        "path": {
            "init": "Initial Path",
            "best": "Best Path"
        },
        "cost" : "Cost (Total)",
        "p" : "P-Values",
        "T" : "Temperature (K)",
        "N_uav" : "Number of UAVs",
        "cost_p" : "Cost (Priority)",
        "cost_d" : "Cost (Distance)",
        "cost_n" : "Cost (Number of UAVs)",
        "window_costs" : "Cost Analysis",
        "window_general" : "General Statistics",
        "window_geometry" : "Geometrical Representation"
    },
    "lim_percent_inc": 1.05,
    "chr": {
        "loading": "░",
        "loaded": "▓",
        "loadbar-left": "<<",
        "loadbar-right": ">>"
    }
}

def loadbar(size, curr, max):
    ratio = curr/max
    if (ratio < 0):
        ratio = 0
    elif (ratio > 1):
        ratio = 1

    load = round(ratio*size)

    return "Loading... " + constants["chr"]["loadbar-left"] + " " + constants["chr"]["loaded"]*load + constants["chr"]["loading"]*(size-load) + " " + constants["chr"]["loadbar-right"]

import opt_sa

def ord_mag(number):
    return math.floor(math.log(number, 10))

def ceil(number):
    mag = ord_mag(number)
    return math.ceil((number*constants["lim_percent_inc"])/(10**mag))*(10**mag)

def unpack_cells(prob):
    unpacked_high = []
    unpacked_low = []
    for i in range(len(prob.env.priorities)):
        if ( prob.env.priorities[i] == 0 ):
            unpacked_low.append(prob.env.cells[i])
        else:
            unpacked_high.append(prob.env.cells[i])
    return (unpacked_high, unpacked_low)

def unpack_path_multi(prob, sol):
    unpacked_multi = []
    for i in range(sol["uav_count"]):
        division = sol["divisions"]["content"][i]
        path = sol["path_uavs"][i]
        unpacked = unpack_path(prob, path, division["ranges"], division["bases"])
        unpacked_multi.append(unpacked)
    return unpacked_multi

def unpack_path(prob, path, ranges, bases):
    unpacked = []
    for iDiv in range(len(ranges)):
        subpath = [prob.env.bases[bases[iDiv][0]]]
        for iCell in range(ranges[iDiv][0], ranges[iDiv][1] + 1):
            cell_i = path[iCell]
            subpath.append(prob.env.cells[cell_i])
        subpath.append(prob.env.bases[bases[iDiv][1]])
        unpacked.append(subpath)
    return unpacked

def plot_path_multi(ax, path_multi):
    i_color = 0
    for path in path_multi:
        plot_path(ax, path, i_color)
        
        i_color += 1
        if (i_color == len(constants["colors"]["path"])):
            i_color = 0

def plot_path(ax, path, i_color):
    plt.pause(constants["timestep"]["subpath"])
    for subpath in path:
        subpath_x, subpath_y = zip(*subpath)
        ax.plot(subpath_x, subpath_y, marker=",", color=matcolor.to_hex(constants["colors"]["path"][i_color], keep_alpha=True))

        if ( window_count() == 0 ):
            break

        plt.draw()
        plt.pause(constants["timestep"]["subpath"])

def visualize(MH, results, geometry=1):
    print("Visualizing...")

    mat.use('Tkagg')
    plt.ion()

    draw_analytical(MH, results, geometry)

    if ( geometry ):
        draw_geometrical(MH, results)

def draw_analytical_more(MH, results):
    fig = plt.figure()
    fig.canvas.manager.set_window_title(constants["title"]["window_costs"])
    
    ax_cost = fig.add_subplot(2, 2, 1)
    ax_cost_p = fig.add_subplot(2, 2, 2)
    ax_cost_d = fig.add_subplot(2, 2, 3)
    ax_cost_n = fig.add_subplot(2, 2, 4)

    N_iter = len(results["cost"]["all"]) - 1
    i = list(range(N_iter + 1))
    cost_lim = [0, ceil(max(results["cost"]["all"]))]
    cost_p_lim = [0, ceil(max(results["cost"]["p"]))]
    cost_d_lim = [0, ceil(max(results["cost"]["d"]))]
    cost_n_lim = [0, ceil(max(results["cost"]["n"]))]

    draw_analytical_cost(ax_cost, i, results["cost"]["all"], N_iter, cost_lim, constants["title"]["cost"])
    draw_analytical_cost(ax_cost_p, i, results["cost"]["p"], N_iter, cost_p_lim, constants["title"]["cost_p"])
    draw_analytical_cost(ax_cost_d, i, results["cost"]["d"], N_iter, cost_d_lim, constants["title"]["cost_d"])
    draw_analytical_cost(ax_cost_n, i, results["cost"]["n"], N_iter, cost_n_lim, constants["title"]["cost_n"])

    plt.draw()
    plt.pause(constants["timestep"]["analytical"])

def draw_analytical_cost(ax, i, j, N_iter, lim, title):
    ax.plot(i, j)
    ax.set_xlim([0, N_iter])
    ax.set_ylim(lim)
    ax.set_aspect(N_iter/lim[1])
    ax.grid()
    ax.set_title(title, color=constants["colors"]["title"], pad=0, style="italic")

def draw_analytical_init(MH, results):
    fig = plt.figure()
    fig.canvas.manager.set_window_title(constants["title"]["window_general"])

    ax_cost = fig.add_subplot(2, 2, 1)
    ax_T = fig.add_subplot(2, 2, 2)
    ax_N_uav = fig.add_subplot(2, 2, 3)
    ax_p = fig.add_subplot(2, 2, 4)

    N_iter = len(results["T"]) - 1
    i = list(range(N_iter + 1))
    max_cost = max(results["cost"]["all"])

    cost_lim = [0, ceil(max_cost)]
    T_lim = [0, ceil(results["T"][0])]
    N_uav_lim = [0, MH.prob.env.constants["uav"]["max"]+1]

    draw_analytical_cost(ax_cost, i, results["cost"]["all"], N_iter, cost_lim, constants["title"]["cost"])

    ax_T.plot(i, results["T"])
    ax_T.set_xlim([0, N_iter])
    ax_T.set_ylim(T_lim)
    ax_T.set_aspect(N_iter/T_lim[1])
    ax_T.grid()
    ax_T.set_title(constants["title"]["T"], color=constants["colors"]["title"], pad=0, style="italic")

    ax_N_uav.plot(i, results["N_uav"])
    ax_N_uav.set_xlim([0, N_iter])
    ax_N_uav.set_ylim(N_uav_lim)
    ax_N_uav.set_aspect(N_iter/N_uav_lim[1])
    ax_N_uav.grid()
    ax_N_uav.set_title(constants["title"]["N_uav"], color=constants["colors"]["title"], pad=0, style="italic")

    ax_p.scatter(results["p"]["i"], results["p"]["values"], marker=constants["markers"]["p"])
    ax_p.set_xlim([0, N_iter])
    ax_p.set_ylim([0, 1])
    ax_p.set_aspect(N_iter)
    ax_p.grid()
    ax_p.set_title(constants["title"]["p"], color=constants["colors"]["title"], pad=0, style="italic")

    plt.draw()
    plt.pause(constants["timestep"]["analytical"])

def draw_analytical(MH, results, geometry):
    if ( isinstance(MH, opt_sa.SA)):
        draw_analytical_init(MH, results)
    draw_analytical_more(MH, results)

    if ( geometry == 0 ):
        plt.ioff()
        plt.show()

def draw_geometrical(SA, results):
    cells_hi, cells_lo = unpack_cells(SA.prob)
    cells_hi_x, cells_hi_y = zip(*cells_hi)
    cells_lo_x, cells_lo_y = zip(*cells_lo)
    bases_x, bases_y = zip(*SA.prob.env.bases)
    
    env_ax = {
        "cells" : {
            "hi": {
                "x": cells_hi_x,
                "y": cells_hi_y
            },
            "lo": {
                "x": cells_lo_x,
                "y": cells_lo_y
            }
        },
        "bases" : {
            "x": bases_x,
            "y": bases_y
        }
    }

    fig = plt.figure()
    fig.canvas.manager.set_window_title(constants["title"]["window_geometry"])
    ax_init = fig.add_subplot(1, 2, 1)
    ax_best = fig.add_subplot(1, 2, 2)

    major_ticks_x = np.arange(SA.prob.env.bounds["x"][0], SA.prob.env.bounds["x"][1] + 1, constants["grid_major_step"])
    minor_ticks_x = np.arange(SA.prob.env.bounds["x"][0], SA.prob.env.bounds["x"][1] + 1, constants["grid_minor_step"])
    major_ticks_y = np.arange(SA.prob.env.bounds["y"][0], SA.prob.env.bounds["y"][1] + 1, constants["grid_major_step"])
    minor_ticks_y = np.arange(SA.prob.env.bounds["y"][0], SA.prob.env.bounds["y"][1] + 1, constants["grid_minor_step"])

    ax_data = {
        "ticks": {
            "major": {
                "x" : major_ticks_x,
                "y" : major_ticks_y
            },
            "minor": {
                "x" : minor_ticks_x,
                "y" : minor_ticks_y
            }
        }
    }

    unpacked_path_init = unpack_path_multi(SA.prob, results["sol"]["init"])
    unpacked_path_best = unpack_path_multi(SA.prob, results["sol"]["best"])

    draw_geometrical_ax(ax_init, ax_data, get_title(constants["title"]["path"]["init"], results["cost"]["all"][0]), env_ax)
    draw_geometrical_ax(ax_best, ax_data, get_title(constants["title"]["path"]["best"], results["cost"]["best"]), env_ax)

    while (True):
        draw_geometrical_ax(ax_init, ax_data, get_title(constants["title"]["path"]["init"], results["cost"]["all"][0]), env_ax)
        plot_path_multi(ax_init, unpacked_path_init)

        draw_geometrical_ax(ax_best, ax_data, get_title(constants["title"]["path"]["best"], results["cost"]["best"]), env_ax)
        plot_path_multi(ax_best, unpacked_path_best)

        if ( window_count() == 0 ):
            break

def draw_geometrical_ax(ax, ax_data, title, env_ax):
    ax.clear()

    ax.set_xticks(ax_data["ticks"]["major"]["x"])
    ax.set_xticks(ax_data["ticks"]["minor"]["x"], minor=True)
    ax.set_yticks(ax_data["ticks"]["major"]["y"])
    ax.set_yticks(ax_data["ticks"]["minor"]["y"], minor=True)

    ax.grid(which='both')
    ax.grid(which='minor', alpha=0.2)
    ax.grid(which='major', alpha=0.5)
    ax.set_aspect('equal')

    ax.set_title(title, color=constants["colors"]["title"], pad=20, style="italic")

    ax.scatter(env_ax["cells"]["hi"]["x"], env_ax["cells"]["hi"]["y"], marker=constants["markers"]["cell_hi"], color=constants["colors"]["cell_hi"])
    ax.scatter(env_ax["cells"]["lo"]["x"], env_ax["cells"]["lo"]["y"], marker=constants["markers"]["cell_lo"], color=constants["colors"]["cell_lo"])
    ax.scatter(env_ax["bases"]["x"], env_ax["bases"]["y"], marker=constants["markers"]["base"], color=constants["colors"]["base"])

def window_count():
    return len(plt.get_fignums())

def get_title(title, cost):
    return title + " (Cost: " + str(round(cost, 1)) + ")"
