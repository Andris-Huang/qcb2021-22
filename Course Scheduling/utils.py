from matplotlib import pyplot as plt
import numpy as np
import itertools
import random
import dataset
import networkx as nx
import os
#import main

def time_lasted(t):
    if t <= 60:
        return f"{round(t, 3)}s"
    return f"{round(t / 60, 3)}min"

def make_random_graph(n_nodes):
    # Create nodes
    nodes = [str(i) for i in range(n_nodes)] 

    # Create edges
    edges = list(itertools.combinations(range(n_nodes), 2))
    n_edges = len(edges)
    edge_weights = [random.randint(1,10) for _ in edges] # use random ints for edge weights for now, to be changed
    edge_list = [(edges[i][0], edges[i][1], edge_weights[i]) for i in range(n_edges)]

    # Add edges to the graph (also adds nodes)
    edge_labels = {}
    for i in range(len(edges)):
        key = edges[i]
        edge_labels[key] = edge_weights[i]
    
    graph = {
        "n_node": n_nodes,
        "n_edge": n_edges,
        "nodes": nodes,
        "edges": edge_list,
        "edge_labels": edge_labels
        }
    return graph

def updated_graph(nodes, edges):
    """
    Return a new graph based on given nodes and find corresponding edges.
    """
    n_nodes = len(nodes)
    new_edges = list(itertools.combinations(nodes, 2))
    n_edges = len(new_edges)

    edge_list = []
    edge_labels = {}
    for e in new_edges:
        edge_labels[e] = edges[e]
        edge_list.append((e[0], e[1], edges[e]))
    
    graph = {
        "n_node": n_nodes,
        "n_edge": n_edges,
        "nodes": nodes,
        "edges": edge_list,
        "edge_labels": edge_labels
        }
    return graph


def display_result(results):
    """
    Reform results into a list of dicts to be written into files.
    Input:
        results: list of course groups
    Return:
        list of dicts
    """
    final_result = []
    for i in range(len(results)):
        group = {f'Group {i+1}': results[i]}
        final_result.append(group)
    return final_result
    

def plot_log(logs, out_img, out_file):
    """
    Plot graph size vs run time.
    """
    ax = plt.subplots(figsize=(6, 6))[1]
    n_node = np.array([abs(int(i[0])) for i in logs], dtype=np.int8)
    run_time = np.array([i[1] for i in logs], dtype=np.float32)

    csv = dataset.CSV()
    result = [{"Number of Nodes": n_node, "Time (s)": run_time}]
    csv.write(result, out_file)

    ax.scatter(n_node, run_time)
    ax.set_title("Run Time vs Graph Size")
    ax.set_ylabel("Time (s)", fontsize=12)
    ax.set_xlabel("Number of Nodes", fontsize=12)
    plt.tight_layout()
    plt.show()
    plt.savefig(out_img, bbox_inches='tight')


def objective_value(result, nodes, edge_weights):
    """
    Calculate the final objective value optimized.

    Input:
        result: final result groups
        nodes: the nodes from the original graph
        edge_weights: a dictionary with the initial edge weights
    Return:
        Optimized final value and original total weights.
    """
    all_weights = sum([edge_weights[e] for e in edge_weights])
    final_value = all_weights
    for group in result:
        new_group = [nodes.index(i) for i in group]
        edges = list(itertools.combinations(new_group, 2))
        for e in edges:
            try:
                final_value -= edge_weights[e]
            except KeyError:
                final_value -= edge_weights[(e[1], e[0])]
    return all_weights, final_value

def plot_graph(graph, name, output_dir, color_list='0.1'): 
    edges = graph["edges"]
    #edge_labels = graph["edge_labels"]
    nodes = graph["nodes"]

    g = nx.Graph()    
    node_list = list(range(len(nodes)))
    g.add_nodes_from(node_list)
    g.add_weighted_edges_from(edges)
    
    plt.figure(figsize=(5,5))
    pos = nx.spring_layout(g)
    nx.draw_networkx_nodes(g, pos, node_size=15, node_color='0.1')
    nx.draw_networkx_edges(g, pos, alpha=0.05, edge_color='0.3')
    filename = f"{name}.png"
    out_name = os.path.join(output_dir, filename)
    plt.savefig(out_name, bbox_inches='tight')

def plot_final_graph(groups, graph, output_dir):
    nodes = graph["nodes"]
    color_list = list(nodes)
    
    new_edges = []
    i = 0
    for group in groups:
        new_group = []
        r, g, b = random.randint(1, 255), random.randint(1, 255), random.randint(1,255)
        for n in group:
            j = nodes.index(n)
            color_list[j] = (r/255, g/255, b/255)
            new_group.append(j)
        e = list(itertools.combinations(new_group, 2))
        new_edges += e
        i += 1
    
    edges = graph["edge_labels"]
    edge_list = []
    edge_labels = {}
    for e in new_edges:
        edge_labels[e] = edges[e]
        edge_list.append((e[0], e[1], edges[e]))

    new_graph = {
        "n_node": len(nodes),
        "n_edge": len(new_edges),
        "nodes": nodes,
        "edges": edge_list,
        "edge_labels": edge_labels
        }

    plot_graph(new_graph, "Output Graph", output_dir, color_list=color_list)
    return new_graph
        
