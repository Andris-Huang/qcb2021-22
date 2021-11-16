from matplotlib import pyplot as plt
import numpy as np
import itertools
import random
import dataset

def time_lasted(t):
    if t <= 60:
        return f"{round(t, 3)} s"
    return f"{round(t / 60, 3)} min"

def make_random_graph(n_nodes):
    # Create nodes
    nodes = list(range(n_nodes)) 

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