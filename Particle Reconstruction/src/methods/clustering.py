# Copyright 2020 D-Wave Systems Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import math
import os
import itertools
import numpy as np

import dwavebinarycsp
import dwave.inspector
from dwave.system import EmbeddingComposite, DWaveSampler

from collections import defaultdict
import matplotlib
matplotlib.use("agg")
import matplotlib.pyplot as plt


class Coordinate:
    def __init__(self, x, y):
        self.x = x
        self.y = y

        # coordinate labels for groups red, green, and blue
        label = "{0},{1}_".format(x, y)
        self.r = label + "r"
        self.g = label + "g"
        self.b = label + "b"
           
def get_distance(coordinate_0, coordinate_1):
    diff_x = coordinate_0.x - coordinate_1.x
    diff_y = coordinate_0.y - coordinate_1.y

    return math.sqrt(diff_x**2 + diff_y**2)


def get_max_distance(coordinates):
    max_distance = 0
    for i, coord0 in enumerate(coordinates[:-1]):
        for coord1 in coordinates[i+1:]:
            distance = get_distance(coord0, coord1)
            max_distance = max(max_distance, distance)

    return max_distance

def get_groupings(sample, nodes):
    """Grab selected items and group them by color"""
    colored_points = defaultdict(list)

    for label, bool_val in sample.items():
        # Skip over items that were not selected
        if not bool_val:
            continue

        # Parse selected items
        # Note: label look like "<x_coord>,<y_coord>_<color>"
        coord, color = label.split("_")
        coord_tuple = tuple(map(float, coord.split(",")))
        colored_points[color].append(coord_tuple)
    all_groups = dict(colored_points)
    final_groups = []
    for color in all_groups:
        group = all_groups[color]
        final_group = []
        for point in group:
            final_group.append(nodes.tolist().index(list(point)))
        final_groups.append(final_group)

    return all_groups, final_groups


def visualize_groupings(groupings_dict, filename):
    """
    Args:
        groupings_dict: key is a color, value is a list of x-y coordinate tuples.
          For example, {'r': [(0,1), (2,3)], 'b': [(8,3)]}
        filename: name of the file to save plot in
    """
    for color, points in groupings_dict.items():
        # Ignore items that do not contain any coordinates
        if not points:
            continue

        # Populate plot
        point_style = color + "o"
        plt.plot(*zip(*points), point_style)

    plt.savefig(filename)


def visualize_scatterplot(x_y_tuples_list, filename):
    """Plotting out a list of x-y tuples

    Args:
        x_y_tuples_list: A list of x-y coordinate values. e.g. [(1,4), (3, 2)]
    """
    plt.plot(*zip(*x_y_tuples_list), "o")
    plt.savefig(filename)


def cluster_points(scattered_points, chainstrength=4, numruns=1000, problem_inspector=False):
    """Perform clustering analysis on given points

    Args:
        scattered_points (list of tuples):
            Points to be clustered
        filename (str):
            Output file for graphic
        problem_inspector (bool):
            Whether to show problem inspector
    """
    # Set up problem
    # Note: max_distance gets used in division later on. Hence, the max(.., 1)
    #   is used to prevent a division by zero
    coordinates = [Coordinate(x, y) for x, y in scattered_points]
    max_distance = max(get_max_distance(coordinates), 1)

    # Build constraints
    csp = dwavebinarycsp.ConstraintSatisfactionProblem(dwavebinarycsp.BINARY)

    # Apply constraint: coordinate can only be in one colour group
    choose_one_group = {(0, 0, 1), (0, 1, 0), (1, 0, 0)}
    for coord in coordinates:
        csp.add_constraint(choose_one_group, (coord.r, coord.g, coord.b))

    # Build initial BQM
    bqm = dwavebinarycsp.stitch(csp)

    # Edit BQM to bias for close together points to share the same color
    for i, coord0 in enumerate(coordinates[:-1]):
        for coord1 in coordinates[i+1:]:
            # Set up weight
            d = get_distance(coord0, coord1) / max_distance  # rescale distance
            weight = -math.cos(d*math.pi)

            # Apply weights to BQM
            bqm.add_interaction(coord0.r, coord1.r, weight)
            bqm.add_interaction(coord0.g, coord1.g, weight)
            bqm.add_interaction(coord0.b, coord1.b, weight)

    # Edit BQM to bias for far away points to have different colors
    for i, coord0 in enumerate(coordinates[:-1]):
        for coord1 in coordinates[i+1:]:
            # Set up weight
            # Note: rescaled and applied square root so that far off distances
            #   are all weighted approximately the same
            d = math.sqrt(get_distance(coord0, coord1) / max_distance)
            weight = -math.tanh(d) * 0.1

            # Apply weights to BQM
            bqm.add_interaction(coord0.r, coord1.b, weight)
            bqm.add_interaction(coord0.r, coord1.g, weight)
            bqm.add_interaction(coord0.b, coord1.r, weight)
            bqm.add_interaction(coord0.b, coord1.g, weight)
            bqm.add_interaction(coord0.g, coord1.r, weight)
            bqm.add_interaction(coord0.g, coord1.b, weight)

    # Submit problem to D-Wave sampler
    sampler = EmbeddingComposite(DWaveSampler())
    sampleset = sampler.sample(bqm,
                               chain_strength=chainstrength,
                               num_reads=numruns,
                               label='Example - Clustering')
    best_sample = sampleset.first.sample

    # Visualize graph problem
    if problem_inspector:
        dwave.inspector.show(bqm, sampleset)

    # Visualize solution
    return get_groupings(best_sample, scattered_points)
    


def solver(graph, output_dir, save_fig=False, 
           print_result=False, config=None, return_edge=False):
    
    scattered_points = graph["nodes"]
    count = 0
    while True:
        filename = f"Input Graph {count}.png"
        orig_filename = os.path.join(output_dir, filename)
        if os.path.exists(orig_filename):
            count += 1
        else:
            break
    if save_fig:
        plt.figure()
        visualize_scatterplot(scattered_points, orig_filename)

    filename = f"Output Graph {count}.png"
    clustered_filename = os.path.join(output_dir, filename)

    try:
        chainstrength = config.chain_strength
    except:
        chainstrength = 4
    try:
        numruns = config.num_runs
    except:
        numruns = 1000

    color_groups, groups = cluster_points(scattered_points, 
                                          chainstrength=chainstrength, 
                                          numruns=numruns)
    if save_fig:
        visualize_groupings(color_groups, clustered_filename)
    if return_edge:
        all_edges = []
        for group in groups:
            all_edges.extend(itertools.combinations(group, 2))
        return all_edges
    return groups

