import itertools
import importlib

base_file = importlib.import_module(f"src.models.base")
Base = base_file.Base
class Model(Base):

    def make_graph(self, event, vars):
        if event.nJets < 3 or event.truthTauN != 2:
            return None
        
        if len([i for i in event.JetIsTautagged if i == 1]) != 2:
            return None

        nodes = [i for i in range(event.nJets)] # FIXME
        n_nodes = len(nodes)

        weighted_edges = []
        edge_dict = {}
        all_edges = list(itertools.combinations(range(n_nodes), 2))
        n_edges = len(all_edges)
        
        edge_score = 0 # TODO
        for i in range(n_edges):
            e = all_edges[i]
            weighted_edges[i] = (e[0], e[1], edge_score)
            edge_dict[e] = edge_score
        
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