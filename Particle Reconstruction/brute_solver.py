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
                 print_result=False, config=None, return_edge=False,
                 disable_tqdm=True):

    n_nodes = graph["n_node"]
    edges = graph["edges"]
    edge_labels = graph["edge_labels"]
    v_num = n_nodes
    G = nx.Graph()
    edges = graph["edges"]
    G.add_weighted_edges_from(edges)

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

    adj = nx.to_numpy_matrix(G)
    best_cost = -1e6
    steps = tqdm.trange(2**v_num, desc=">>> Solving Progress", disable=disable_tqdm)
    for b in steps:
        x = [int(t) for t in list(bin(b)[2:].zfill(v_num))]
        cost = 0
        if all([i==0 for i in x]) or all([i==1 for i in x]):
            continue
        for i in range(v_num):
            for j in range(v_num):
                cost += adj[i, j]*x[i]*(1-x[j])
        if best_cost < cost:
            best_cost = cost
            x_best = x

    S0 = [node for node in G.nodes if x_best[node]==0]
    S1 = [node for node in G.nodes if x_best[node]==1]
    cut_edges = [(u, v) for u, v in G.edges if x_best[u]!=x_best[v]]
    uncut_edges = [(u, v) for u, v in G.edges if x_best[u]==x_best[v]]

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