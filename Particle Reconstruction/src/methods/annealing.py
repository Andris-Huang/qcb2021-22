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
import os
import itertools
import random
import importlib

dataset = importlib.import_module("dataset")
utils = importlib.import_module("utils")
import time


def solver(graph, output_dir, save_fig=False, 
           print_result=False, config=None, return_edge=False):
    """
    Perform the max-cut solver by dwave and return the graph size and solving time.
    Input:
        graph: graph input
        output_dir: the output directory
        save_fig: save the figure iff true
        print_result: boolean for display grouping result
    Return:
        result: [S0, S1], node index for two groups
    """

    n_nodes = graph["n_node"]
    edges = graph["edges"]
    edge_labels = graph["edge_labels"]

    # ------- Set up our graph -------

    # Create empty graph
    G = nx.Graph()

    # Add attritubes to the graph
    G.add_weighted_edges_from(edges)

    # Save the graph beforehand for testing/demo purposes
    if save_fig:
        g = G.copy()
        plt.figure()
        pos = nx.spring_layout(G)
        if n_nodes <= 10:
            nx.draw_networkx(g, pos, node_color='r')
            nx.draw_networkx_edge_labels(g, pos, edge_labels=edge_labels)
        else:
            nx.draw_networkx_nodes(g, pos, node_size=15, node_color='0.1')
            nx.draw_networkx_edges(g, pos, alpha=0.05, edge_color='0.3')
        count = 0
        while True:
            filename = f"Input Graph {count}.png"
            out_name = os.path.join(output_dir, filename)
            if os.path.exists(out_name):
                count += 1
            else:
                break
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
    try:
        chainstrength = config.chain_strength
    except:
        chainstrength = 2
    try:
        numruns = config.num_runs
    except:
        numruns = 10

    # Run the QUBO on the solver from your config file
    #start = time.time()
    #print(">>> Graph created successfully, start solving max-cut")

    sampler = EmbeddingComposite(DWaveSampler())
    response = sampler.sample_ising(h, J,
                                    chain_strength=chainstrength,
                                    num_reads=numruns,
                                    label='Maximum Cut Ising')

    # ------- Print results to user -------
    if print_result:
        print('-' * 60)
        print('{:>15s}{:>15s}{:^15s}{:^15s}'.format('Set 0','Set 1','Energy','Cut Size'))
        print('-' * 60)
        for sample, E in response.data(fields=['sample','energy']):
            S0 = [k for k,v in sample.items() if v == -1]
            S1 = [k for k,v in sample.items() if v == 1]
            print('{:>15s}{:>15s}{:^15s}{:^15s}'.format(str(S0),str(S1),str(E),str(int((6-E)/2))))

    #end = time.time()
    #dt = end - start
    #delta_t = utils.time_lasted(dt)
    #print(f">>> Grouping finished, total time: {delta_t}")
    

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
    if save_fig:
        plt.figure()
        if n_nodes <= 10:
            nx.draw_networkx_nodes(G, pos, nodelist=S0, node_color='r')
            nx.draw_networkx_nodes(G, pos, nodelist=S1, node_color='b')
            nx.draw_networkx_edges(G, pos, edgelist=cut_edges, style='dashdot', alpha=0.5, width=3)
            nx.draw_networkx_edges(G, pos, edgelist=uncut_edges, style='solid', width=3)
            nx.draw_networkx_edge_labels(g, pos, edge_labels=edge_labels)
            nx.draw_networkx_labels(G, pos)
        else:
            nx.draw_networkx_nodes(G, pos, nodelist=S0, node_size=15, node_color='r')
            nx.draw_networkx_nodes(G, pos, nodelist=S1, node_size=15, node_color='b')
            nx.draw_networkx_edges(G, pos, edgelist=uncut_edges, alpha=0.05, edge_color='0.3')

        filename = f"Output Graph {count}.png"
        out_name = os.path.join(output_dir, filename)
        plt.savefig(out_name, bbox_inches='tight')

    if return_edge:
        return uncut_edges
    return S0, S1