# Copyright 2019 D-Wave Systems, Inc.
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

# ------- Import necessary packages -------
from collections import defaultdict
from dwave.system.samplers import DWaveSampler
from dwave.system.composites import EmbeddingComposite

from matplotlib import pyplot as plt
import networkx as nx
import argparse
import os
import itertools
import random

import dataset
import annealing
import utils
import time

# ------- Add terminal commands -------
parser = argparse.ArgumentParser(description='Train GNN')
add_arg = parser.add_argument
add_arg("-in", "--input-dir", help="Input graph directory", default="inputs/Random Course.csv")
add_arg("-s","--save-fig", help="Save resulting image if True", default=False)
add_arg("-o", "--output-dir", help="Output graph directory", default="outputs")
add_arg("-n", "--num", help="Number of nodes in a random graph", type=int, default=10)
add_arg("--threshold", help="Max number of course in a group", type=int, default=10)
add_arg("--log", help="Write log iff True", default=True)
add_arg("--overwrite", help="Overwrite plot and log files iff true", default=False)

args = parser.parse_args()

inname = args.input_dir
save_fig = bool(args.save_fig)
write_log = bool(args.log)
outname = args.output_dir
cwd = os.path.dirname(os.path.abspath(__file__))
input_dir = os.path.join(cwd, inname)
output_dir = os.path.join(cwd, outname)
threshold = args.threshold

if os.path.exists(output_dir):
    print(f">>> Use existing output directory\n>>> Path: {output_dir}")
else:
    os.makedirs(output_dir, exist_ok=True)
    print(f">>> Output directory created\n>>> Path: {output_dir}")

# ------- Load dataset -------
csv = dataset.CSV()
if os.path.exists(input_dir):
    print(f">>> Using inputs from {input_dir}")
    data = csv.read(input_dir)
    graph = csv.make_graph(data)
else:
    print(">>> Using a random graph")
    n_nodes = args.num
    graph = utils.make_random_graph(n_nodes=n_nodes)

nodes = graph["nodes"]
edge_weights = graph["edge_labels"]
all_log = []

def recursive_solver(graph, solver, threshold=threshold, save_fig=save_fig, debug=False):
    """
    Recursively conduct max-cut solver.
    Input:
        graph: graph
        solver: the solving algorithm used
        result_count: How many time max-cut has run
        threshold: up to how many courses can be in a group, default=10
    Return:
        list of course groups
    """
    if graph["n_node"] <= threshold:
        return [[nodes[int(i)] for i in graph["nodes"]]]

    result, log = solver(graph, output_dir, save_fig=save_fig)
    all_log.append(log)
    S0, S1 = result
    G0 = utils.updated_graph(S0, edge_weights)
    G1 = utils.updated_graph(S1, edge_weights)
    if debug:
        print(G0['edges'])
    return recursive_solver(G0, solver) + recursive_solver(G1, solver)

results = recursive_solver(graph, annealing.max_cut_solver)
final_result = utils.display_result(results)

result_name = f"Result.csv"
result_file = os.path.join(output_dir, result_name)
csv.write(final_result, result_file)

objective = utils.objective_value(results, edge_weights)
print(f">>> Reduced Number of Conclicts: {objective}")

count = 0
while not args.overwrite:
    log_name = f"Run Time {count}.png"
    log_img = os.path.join(output_dir, log_name)
    log_name2 = f"Run Time {count}.csv"
    log_file = os.path.join(output_dir, log_name2)
    if os.path.exists(log_img) or os.path.exists(log_file):
        count += 1
    else:
        break
else:
    log_name = f"Run Time {count}.png"
    log_img = os.path.join(output_dir, log_name)
    log_name2 = f"Run Time {count}.csv"
    log_file = os.path.join(output_dir, log_name2)

if write_log:
    utils.plot_log(all_log, log_img, log_file)