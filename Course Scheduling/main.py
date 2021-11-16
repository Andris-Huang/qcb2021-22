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
args = parser.parse_args()

inname = args.input_dir
save_fig = args.save_fig
outname = args.output_dir
cwd = os.path.dirname(os.path.abspath(__file__))
input_dir = os.path.join(cwd, inname)
output_dir = os.path.join(cwd, outname)

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
    graph = utils.make_random_graph(n_nodes=10)

nodes = graph["nodes"]
edge_weights = graph["edge_labels"]
all_log = []

def recursive_solver(graph, threshold=10, save_fig=save_fig, debug=False):
    """
    Recursively conduct max-cut solver.
    Input:
        graph: graph
        result_count: How many time max-cut has run
        threshold: up to how many courses can be in a group, default=10
    Return:
        list of course groups
    """
    if graph["n_node"] <= threshold:
        return [[nodes[int(i)] for i in graph["nodes"]]]

    result, log = annealing.max_cut_solver(graph, output_dir, save_fig=save_fig)
    all_log.append(log)
    S0, S1 = result
    G0 = utils.updated_graph(S0, edge_weights)
    G1 = utils.updated_graph(S1, edge_weights)
    if debug:
        print(G0['edges'])
    return recursive_solver(G0) + recursive_solver(G1)


results = recursive_solver(graph)
final_result = utils.display_result(results)

result_name = f"Result.csv"
result_file = os.path.join(output_dir, result_name)
csv.write(final_result, result_file)

log_name = "Run Time.png"
log_img = os.path.join(output_dir, log_name)
log_name2 = "Run Time.csv"
log_file = os.path.join(output_dir, log_name2)
utils.plot_log(all_log, log_img, log_file)