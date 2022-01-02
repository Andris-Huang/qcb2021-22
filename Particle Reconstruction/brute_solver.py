from matplotlib import pyplot as plt
import networkx as nx
import os
import itertools
import random

import dataset
import utils
import time
import tqdm

def brute_solver(graph, output_dir, save_fig=False, 
                 print_result=False, config=None, return_edge=False):

    n_nodes = graph["n_node"]
    edges = graph["edges"]
    edge_labels = graph["edge_labels"]
    v_num = n_nodes
    G = nx.Graph()
    edges = graph["edges"]
    G.add_weighted_edges_from(edges)

    if save_fig:
        if n_nodes <= 10:
            g = G.copy()
            plt.figure()
            pos = nx.spring_layout(G)
            nx.draw_networkx(g, pos, node_color='r')
            nx.draw_networkx_edge_labels(g, pos, edge_labels=edge_labels)
            filename = "Input Graph.png"
            out_name = os.path.join(output_dir, filename)
            plt.savefig(out_name, bbox_inches='tight')
            print(f">>> The plot {filename} is saved to {out_name}")
        else:
            utils.plot_graph(graph, "Input Graph", output_dir)

    adj = nx.to_numpy_matrix(G)
    best_cost = -1e6
    steps = tqdm.trange(10000, desc="Solving Progress")
    step_size = 2**v_num//10000
    for i in steps:
        for b in range(i*step_size, (i+1)*step_size):
            x = [int(t) for t in list(bin(b)[2:].zfill(v_num))]
            cost = 0
            for i in range(v_num):
                for j in range(v_num):
                    cost = cost + adj[i, j]*x[i]*(1-x[j])
            if best_cost < cost:
                best_cost = cost
                x_best = x

    S0 = [node for node in G.nodes if x_best[node]==-1]
    S1 = [node for node in G.nodes if x_best[node]==1]
    cut_edges = [(u, v) for u, v in G.edges if x_best[u]!=x_best[v]]
    uncut_edges = [(u, v) for u, v in G.edges if x_best[u]==x_best[v]]
    if save_fig:
        if n_nodes <= 10:
            plt.figure()
            nx.draw_networkx_nodes(G, pos, nodelist=S0, node_color='r')
            nx.draw_networkx_nodes(G, pos, nodelist=S1, node_color='c')
            nx.draw_networkx_edges(G, pos, edgelist=cut_edges, style='dashdot', alpha=0.5, width=3)
            nx.draw_networkx_edges(G, pos, edgelist=uncut_edges, style='solid', width=3)
            nx.draw_networkx_edge_labels(g, pos, edge_labels=edge_labels)
            nx.draw_networkx_labels(G, pos)

            filename = "Output Graph.png"
            out_name = os.path.join(output_dir, filename)
            plt.savefig(out_name, bbox_inches='tight')
            print(f">>> The plot {filename} is saved to {out_name}")
        else:
            utils.plot_final_graph([S0, S1], graph, output_dir)

    return uncut_edges