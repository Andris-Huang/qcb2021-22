import itertools
import importlib
import numpy as np


base_file = importlib.import_module(f"src.models.base")
Base = base_file.Base
class Model(Base):

    def make_graph(self, event, debug=False):
        scale = 0.001
        n_node_features = 7
        # information of each particle: px, py, pz, E, pdgID, isFromW, isInLeadingJet
        n_nodes = len(event) // n_node_features
        if n_nodes > 80:
            return None

        nodes = [[
            event[inode*n_node_features+0], # px
            event[inode*n_node_features+1], # py
            event[inode*n_node_features+2], # pz
            event[inode*n_node_features+3]  # E
        ] for inode in range(n_nodes) ]

        node_target = [
            event[inode*n_node_features+5] # isFromW
            for inode in range(n_nodes)
        ]

        nodes = np.array(nodes, dtype=np.float32) / scale
        node_target = np.array(node_target, dtype=np.float32)
        true_nodes = np.where(node_target==1)[0].tolist()
        node_target = np.expand_dims(node_target, axis=1)

        all_edges = list(itertools.combinations(range(n_nodes), 2))
        n_edges = len(all_edges)
        #edges = np.expand_dims(np.array([0.0]*n_edges, dtype=np.float32), axis=1)

        edge_target = [
            int(edge[0] in true_nodes and edge[1] in true_nodes)
            for edge in all_edges
        ]

        #edge_target = np.expand_dims(np.array(edge_target, dtype=np.float32), axis=1)

        weighted_edges = []
        edge_dict = {}
        for i in range(n_edges):
            e = all_edges[i]
            edge_score = 1 - np.dot(np.linalg.norm(nodes[e[0]]), np.linalg.norm(nodes[e[1]]))
            if debug:
                edge_score = 1- edge_target[i]
            weighted_edges.append((e[0], e[1], edge_score))
            edge_dict[e] = edge_score

        graph = {
            "n_node": n_nodes,
            "n_edge": n_edges,
            "nodes": [i for i in range(n_nodes)],
            "edges": weighted_edges,
            "edge_labels": edge_dict,
            "truth": edge_target
            }
        
        if debug:
            print(n_nodes)
            print(edge_target)
        
        return graph

    def predict(self, solver, graph):
        """
        Predict clusters given solver and event
        """
        uncut_edges = solver(graph, self.output_dir, self.save_fig, 
                             config=self.config, return_edge=True)
        pred = []
        edge_dict = graph["edge_labels"]
        for e in edge_dict:
            if e in uncut_edges:
                pred.append(1)
            else:
                pred.append(0)

        return pred