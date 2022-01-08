import itertools
import importlib
import numpy as np

utils = importlib.import_module("utils")
base_file = importlib.import_module(f"src.models.base")
Base = base_file.Base
class Model(Base):

    def make_graph(self, event, debug=False, *args, **kwargs):
        if event.nTauJets > 1 or event.nJets == event.nTauJets:
            return None

        scale_factors = np.array([1.0e-3,1.0/3.0,1.0/np.pi], dtype=np.float32)

        nTaus = 0

        nodes = []
        node_target = []
        for ijet in range(event.nJets):
            # Match jet to truth jet that minimizes angular distance
            min_index = 0
            if event.nTruthJets > 0:
                min_dR = np.sqrt((event.JetPhi[ijet]-event.TruthJetPhi[0])**2 + (event.JetEta[ijet]-event.TruthJetEta[0])**2)
            for itruth in range(event.nTruthJets):
                dR = np.sqrt((event.JetPhi[ijet]-event.TruthJetPhi[itruth])**2 + (event.JetEta[ijet]-event.TruthJetEta[itruth])**2)
                if dR < min_dR:
                    min_dR = dR
                    min_index = itruth
            if event.nTruthJets > 0 and min_dR < 0.4:
                isTau = int(event.TruthJetIsTautagged[min_index] > 0)
            else:
                isTau = 0

            nodes.append(utils.get_jet_info(event, ijet))
            node_target.append(isTau)

            nTaus += isTau

        n_nodes = len(nodes)
        if n_nodes > 15 or nTaus == event.nJets or n_nodes < 2 or nTaus> 1 or nTaus < 0:
            return None

        nodes = np.array(nodes, dtype=np.float32) * scale_factors
        node_target = np.array(node_target, dtype=np.float32)
        
        if debug:
            if n_nodes != 2:
                return None

        node_target = np.expand_dims(node_target, axis=1)

        all_edges = list(itertools.combinations(range(n_nodes), 2))
        n_edges = len(all_edges)

        edge_target = [
            int(node_target[edge[0]] == node_target[edge[1]])
            for edge in all_edges
        ]
        #edge_target = np.expand_dims(np.array(edge_target, dtype=np.float32), axis=1)

        weighted_edges = []
        edge_dict = {}
        for i in range(n_edges):
            e = all_edges[i]
            edge_score = -np.dot(np.linalg.norm(nodes[e[0]]), np.linalg.norm(nodes[e[1]]))
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
            print(f"***n_nodes: {n_nodes}***")
            print(f"***edge_target:{edge_target}***")
            print(f"***node_target: {node_target}***")
        
        return [graph]


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