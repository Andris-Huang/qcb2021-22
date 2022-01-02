import itertools
import importlib

base_file = importlib.import_module(f"src.models.base")
Base = base_file.Base
class Model(Base):
    def __init__(self, data, num_evts, output_dir, save_fig, config=None, debug=False):
        super().__init__(data, num_evts, output_dir, save_fig, config, debug)
        
    def make_graph(self, event, debug=False):
        if event.nJets < 3 or event.truthTauN != 2:
            return None
        
        if len([i for i in event.JetIsTautagged if i == 1]) != 2:
            return None
        
        Pt1, Pt2 = event.truthTauEt[0], event.truthTauEt[1]
        eta1, eta2 = event.truthTauEta[0], event.truthTauEta[1]
        phi1, phi2 = event.truthTauPhi[0], event.truthTauPhi[1]
        true_M = self._calc_mass(Pt1, Pt2, eta1, eta2, phi1, phi2)

        nodes = [i for i in range(event.nJets)]
        n_nodes = len(nodes)

        weighted_edges = []
        edge_dict = {}
        all_edges = list(itertools.combinations(range(n_nodes), 2))
        n_edges = len(all_edges)

        min_edge_score = 1e6
        for edge in all_edges:
            Pt1, eta1, phi1 = self._get_jet_info(event, edge[0])
            Pt2, eta2, phi2 = self._get_jet_info(event, edge[1])
            calc_M = self._calc_mass(Pt1, Pt2, eta1, eta2, phi1, phi2)
            edge_score = abs(int(true_M - calc_M))
            if edge_score < min_edge_score:
                min_edge_score = edge_score
            weighted_edges.append((edge[0], edge[1], edge_score))
            edge_dict[edge] = edge_score
        
        
        for i in range(n_edges):
            e = all_edges[i]
            if weighted_edges[i][2] != min_edge_score:
                weighted_edges[i] = (e[0], e[1], 1e6)
                edge_dict[e] = 1e6
        
        if len(event.TruthJetIsTautagged) != n_nodes:
            return None
            
        truth = []
        for i in event.TruthJetIsTautagged:
            if i == 0:
                truth.append(0)
            else:
                truth.append(1)

        graph = {
            "n_node": n_nodes,
            "n_edge": n_edges,
            "nodes": nodes,
            "edges": weighted_edges,
            "edge_labels": edge_dict,
            "truth": truth
            }
        
        return graph

    def predict(self, solver, graph):
        """
        Brute force prediction.
        """
        nodes = graph["nodes"]
        pred = [0 for _ in nodes]
        edges = graph["edge_labels"]
        for e in edges:
            if edges[e] != 1e6:
                pred[e[0]] = pred[e[1]] = 1
        return pred