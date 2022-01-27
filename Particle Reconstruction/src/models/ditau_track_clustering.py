import itertools
import importlib
import numpy as np
import time
import tqdm

utils = importlib.import_module("utils")
base_file = importlib.import_module(f"src.models.base")
Base = base_file.Base

class Model(Base):

    def make_graph(self, event, debug=False, **kwargs):

        config = self.config
        score_method = "cos_similarity" if isinstance(config.model_name, str) else config.model_name[1]
        calc_edge_score = getattr(utils, score_method)
        
        if event.nJets > 3 or event.nJets < 2:
            return None

        track_idx = 0

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

            for _ in range(event.JetGhostTrackN[ijet]):
                ghost_track_idx = event.JetGhostTrackIdx[track_idx]
                nodes.append(utils.get_track_info(event, ghost_track_idx)[1:])
                node_target.append(ijet)
                track_idx+=1

            nTaus += isTau

        n_nodes = len(nodes)
        if n_nodes < 4:
            return None

        nodes = np.array(nodes, dtype=np.float32)
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
        try:
            use_pt = config.use_pt
        except:
            use_pt = True

        weighted_edges = []
        edge_dict = {}
        for i in range(n_edges):
            e = all_edges[i]
            v1, v2 = (nodes[e[0]], nodes[e[1]]) if use_pt else (nodes[e[0]][1:], nodes[e[1]][1:])
            edge_score = calc_edge_score(v1, v2)
            weighted_edges.append((e[0], e[1], edge_score))
            edge_dict[e] = edge_score

        graph = {
            "n_node": n_nodes,
            "n_edge": n_edges,
            "nodes": nodes,
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


    def get_results(self, solver, display_efficiency=False):
        """
        Overwrite the get_results function with display_efficiency
        always set to false.
        """
        return super().get_results(solver, display_efficiency=False)
