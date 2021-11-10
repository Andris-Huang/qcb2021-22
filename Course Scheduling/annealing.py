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

# ------- Add terminal commands -------
parser = argparse.ArgumentParser(description='Train GNN')
add_arg = parser.add_argument
add_arg("-in", "--input-dir", help="Input graph directory", default=None)
add_arg("-s","--save-fig", help="Save resulting image if True", default=True)
add_arg("-o", "--output-dir", help="Output graph directory", default="outputs")
args = parser.parse_args()

input_dir = args.input_dir
save_fig = args.save_fig
outname = args.output_dir
cwd = os.path.dirname(os.path.abspath(__file__))
output_dir = os.path.join(cwd, outname)

if os.path.exists(output_dir):
    print(f">>> Use existing output directory >>>\nPath: {output_dir}")
else:
    os.makedirs(output_dir, exist_ok=True)
    print(f">>> Output directory created >>>\nPath: {output_dir}")


# ------- Set up our graph -------

# Create empty graph
G = nx.Graph()

# Create nodes
n_nodes = 7 # random number, to be changed
nodes = list(range(n_nodes)) 

# Create edges
edges = list(itertools.combinations(range(n_nodes), 2))
edge_weights = [random.randint(1,10) for _ in edges] # use random ints for edge weights for now, to be changed
edge_list = [(edges[i][0], edges[i][1], edge_weights[i]) for i in range(len(edges))]

# Add edges to the graph (also adds nodes)
edge_labels = {}
for i in range(len(edges)):
    key = edges[i]
    edge_labels[key] = edge_weights[i]
G.add_weighted_edges_from(edge_list)

# Save the graph beforehand for testing purposes
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
sampler = EmbeddingComposite(DWaveSampler())
response = sampler.sample_ising(h, J,
                                chain_strength=chainstrength,
                                num_reads=numruns,
                                label='Example - Maximum Cut Ising')

# ------- Print results to user -------
print('-' * 60)
print('{:>15s}{:>15s}{:^15s}{:^15s}'.format('Set 0','Set 1','Energy','Cut Size'))
print('-' * 60)
for sample, E in response.data(fields=['sample','energy']):
    S0 = [k for k,v in sample.items() if v == -1]
    S1 = [k for k,v in sample.items() if v == 1]
    print('{:>15s}{:>15s}{:^15s}{:^15s}'.format(str(S0),str(S1),str(E),str(int((6-E)/2))))


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

# Display best result
plt.figure()
nx.draw_networkx_nodes(G, pos, nodelist=S0, node_color='r')
nx.draw_networkx_nodes(G, pos, nodelist=S1, node_color='c')
nx.draw_networkx_edges(G, pos, edgelist=cut_edges, style='dashdot', alpha=0.5, width=3)
nx.draw_networkx_edges(G, pos, edgelist=uncut_edges, style='solid', width=3)
nx.draw_networkx_edge_labels(g, pos, edge_labels=edge_labels)
nx.draw_networkx_labels(G, pos)

filename = "Output Graph.png"
out_name = os.path.join(output_dir, filename)
plt.show()
if save_fig:
    plt.savefig(out_name, bbox_inches='tight')
    print("\nYour plot is saved to {}".format(out_name))