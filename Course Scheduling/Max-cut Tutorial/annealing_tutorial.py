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
import utils
import time

# ------- Add terminal commands -------
parser = argparse.ArgumentParser(description='Train GNN')
add_arg = parser.add_argument
add_arg("-in", "--input-dir", help="Input graph directory", default="inputs/Random Course.csv")
add_arg("-s","--save-fig", help="Save resulting image if True", default=True)
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
n_nodes = graph["n_node"]
edges = graph["edges"]
edge_labels = graph["edge_labels"]

plot_fig = n_nodes <= 10
save_fig = save_fig and plot_fig

# ------- Set up our graph -------

# Create empty graph
G = nx.Graph()

# Add attritubes to the graph
G.add_weighted_edges_from(edges)

# Save the graph beforehand for testing purposes
if save_fig:
    g = G.copy()
    plt.figure()
    pos = nx.spring_layout(G)
    nx.draw_networkx(g, pos, node_color='r')
    nx.draw_networkx_edge_labels(g, pos, edge_labels=edge_labels)
    filename = "Input Graph.png"
    out_name = os.path.join(output_dir, filename)
    plt.savefig(out_name, bbox_inches='tight')

# ------- Set up our QUBO dictionary -------

# Initialize our h vector, J matrix
h = defaultdict(int)
J = defaultdict(int)

# Update J matrix for every edge in the graph
for i, j in G.edges:
    J[(i,j)]+= 1

# ------- Run our QUBO on the QPU -------
# Set up QPU parameters
chainstrength = 2
numruns = 10

# Run the QUBO on the solver from your config file
start = time.time()
print(">>> Graph created successfully, start solving max-cut")

sampler = EmbeddingComposite(DWaveSampler())
response = sampler.sample_ising(h, J,
                                chain_strength=chainstrength,
                                num_reads=numruns,
                                label='Maximum Cut Ising')

# ------- Print results to user -------
if plot_fig:
    print('-' * 60)
    print('{:>15s}{:>15s}{:^15s}{:^15s}'.format('Set 0','Set 1','Energy','Cut Size'))
    print('-' * 60)
    for sample, E in response.data(fields=['sample','energy']):
        S0 = [k for k,v in sample.items() if v == -1]
        S1 = [k for k,v in sample.items() if v == 1]
        print('{:>15s}{:>15s}{:^15s}{:^15s}'.format(str(S0),str(S1),str(E),str(int((6-E)/2))))

end = time.time()
delta_t = utils.time_lasted(end - start)
print(f">>> Grouping finished, total time: {delta_t}")

# ------- Display results to user -------
# Grab best result
# Note: "best" result is the result with the lowest energy
# Note2: the look up table (lut) is a dictionary, where the key is the node index
#   and the value is the set label. For example, lut[5] = 1, indicates that
#   node 5 is in set 1 (S1).
lut = response.first.sample

# Interpret best result in terms of nodes and edges
S0 = [node for node in G.nodes if lut[node]==-1]
S1 = [node for node in G.nodes if lut[node]==1]
cut_edges = [(u, v) for u, v in G.edges if lut[u]!=lut[v]]
uncut_edges = [(u, v) for u, v in G.edges if lut[u]==lut[v]]
result = [{"Group 1": S0}, {"Group 2": S1}, {"Edge Weights": [edge_labels[e] for e in uncut_edges]}]

# Display best result
if save_fig:
    plt.figure()
    nx.draw_networkx_nodes(G, pos, nodelist=S0, node_color='r')
    nx.draw_networkx_nodes(G, pos, nodelist=S1, node_color='c')
    nx.draw_networkx_edges(G, pos, edgelist=cut_edges, style='dashdot', alpha=0.5, width=3)
    nx.draw_networkx_edges(G, pos, edgelist=uncut_edges, style='solid', width=3)
    nx.draw_networkx_edge_labels(g, pos, edge_labels=edge_labels)
    nx.draw_networkx_labels(G, pos)

filename = "Output Graph.png"
out_name = os.path.join(output_dir, filename)
if plot_fig:
    plt.show()
if save_fig:
    plt.savefig(out_name, bbox_inches='tight')
    print("\n>>> Your plot is saved to {} <<<".format(out_name))

result_count = 0
result_name = f"Result {result_count}.csv"
result_file = os.path.join(output_dir, result_name)
csv.write(result, result_file)
result_count += 1