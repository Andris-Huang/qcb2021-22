import numpy as np
import time
import tqdm
import importlib

utils = config = importlib.import_module("utils")

class Base:
    """
    Base class for models.
    """
    def __init__(self, data, num_evts, output_dir, save_fig, config=None, debug=False):
        self.num_evts = num_evts
        self.graphs = self.process_data(data, debug)
        self.output_dir = output_dir
        self.save_fig = save_fig
        self.results = None
        self.config = config
        try:
            lim = self.config.time_limit
            if lim > 0 and lim != None:
                self.time_limit = lim
            else:
                self.time_limit = 30 * 60
        except:
            self.time_limit = 30 * 60 # default 30min
        display_time = utils.time_lasted(self.time_limit)
        print(f">>> Job Time Limit: {display_time}")

    
    def process_data(self, events, debug):
        """
        Process the data into graphs.
        """
        num_failed = 0
        all_graphs = []
        for event in events:
            graph = self.make_graph(event, debug)
            if graph != None:
                all_graphs.append(graph)
                if len(all_graphs) >= self.num_evts:
                    break
            else:
                num_failed += 1
        self.graphs = all_graphs
        print(f">>> {len(self.graphs)} events successfully processed, {num_failed} events failed to be converted into graphs.")
        return all_graphs
            

    def make_graph(self, event, debug=False):
        """
        Convert the data read into graphs
        """
        raise NotImplementedError


    def predict(self, solver, graph):
        """
        Predict taus given solver and event
        """
        S0, S1 = solver(graph, self.output_dir, self.save_fig, config=self.config)
        if len(S1) == 2:
            S0, S1 = S1, S0
        elif len(S0) != 2:
            print("The maxcut solver has identified wrong number of jets.")
        pred = list(graph["nodes"])
        for n in S0:
            pred[n] = 1
        for n in S1:
            pred[n] = 0
        for i in range(len(pred)):
            if pred[i] != 0 and pred[i] != 1:
                print("Some jets do not have a prediction.")
                pred[i] = 0
        return np.array(pred, dtype=np.int8)


    def get_results(self, solver):
        """
        Get resulting predictions for all data.
        """
        results = []
        start = time.time()
        iter_bar = tqdm.trange(len(self.graphs), desc="Progress")
        for i in iter_bar:
            graph = self.graphs[i]
            n_node = graph["n_node"]
            pred = self.predict(solver, graph)
            results.append(pred)
            self.results = results   
            graphs_so_far = self.graphs[:i+1]
            auc = self.validate(graphs_so_far)
            iter_bar.set_postfix({"ACC": f"{auc:.4f}", 
                                  "Size": n_node})
            now = time.time()
            if (now - start) >= self.time_limit:
                print(">>> Job killed due to time limit")
                break
        self.results = results
        return results


    def validate(self, graphs=None):
        """
        Validatate results.
        """
        if self.results == None:
            print("No predictions made yet!")
            return
        if graphs == None:
            graphs = self.graphs

        num_correct = 0
        total = 0
        for i in range(len(self.results)):
            graph = graphs[i]
            result = self.results[i]
            truth = graph["truth"]
            assert len(result) == len(truth), "mismatch of length between pred and truth"
            for i in range(len(result)):
                if result[i] == truth[i]:
                    num_correct += 1
                total += 1
        return num_correct / total


    def _calc_mass(self, Pt1, Pt2, eta1, eta2, phi1, phi2):
        return np.sqrt(2*Pt1*Pt2*(np.cosh(eta1-eta2)-np.cos(phi1-phi2)))
    
    def _get_jet_info(self, event, idx):
        return [event.JetPt[idx], event.JetEta[idx], event.JetPhi[idx]]

    def _get_track_info(self, event, idx):
        return [event.TrackPt[idx], event.TrackEta[idx], event.TrackPhi[idx]]

    def _get_tower_info(self, event, idx):
        return [event.JetTowerEt[idx], event.JetTowerEta[idx], event.JetTowerPhi[idx]]
