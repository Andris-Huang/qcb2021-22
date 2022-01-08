import numpy as np
import time
import tqdm
import importlib

utils = importlib.import_module("utils")

class Base:
    """
    Base class for models.
    """
    def __init__(self, data, num_evts, output_dir, save_fig, config=None, debug=False):
        self.num_evts = num_evts
        self.config = config
        self.graphs = self.process_data(data, debug)
        self.output_dir = output_dir
        self.save_fig = save_fig
        self.results = None
        self.reference = None
        self.truth = [graph["truth"] for graph in self.graphs]
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
            if graph != None and len(graph) > 0:
                all_graphs.extend(graph)
                if len(all_graphs) >= self.num_evts:
                    break
            else:
                num_failed += 1
        self.graphs = all_graphs
        self.event_ratio = f"{round(len(self.graphs)/(num_failed+len(self.graphs))*100, 2)}%"
        print(f">>> {len(self.graphs)} events successfully processed, " +
                  f"{num_failed} events failed to be converted into graphs. " +
                  f"Success ratio: {self.event_ratio}.")
        return all_graphs
            

    def make_graph(self, event, debug=False, **kwargs):
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


    def get_results(self, solver, display_efficiency=False):
        """
        Get resulting predictions for all data.
        """
        results = []
        reference = []
        start = time.time()
        iter_bar = tqdm.trange(len(self.graphs), desc=">>> Progress")
        for i in iter_bar:
            graph = self.graphs[i]
            n_node = graph["n_node"]
            pred = self.predict(solver, graph)
            results.append(pred)
            self.results = results   
            graphs_so_far = self.graphs[:i+1]
            auc = self.validate(graphs_so_far)
            if display_efficiency:
                brute_solver = importlib.import_module("brute_solver")
                brute = brute_solver.brute_solver
                ref = self.predict(brute, graph)
                reference.append(ref)
                self.reference = reference
                eff = self.validate(graphs_so_far, all_truth=reference)
                max_acc = self.validate(graphs_so_far, all_results=reference)
                iter_bar.set_postfix({"ACC": f"{auc:.4f}", 
                                      "EFF": f"{eff:.4f}",
                                      "MAX_ACC": f"{max_acc:.4f}",
                                      "Size": n_node,})
            else:
                iter_bar.set_postfix({"ACC": f"{auc:.4f}", 
                                      "Size": n_node})
            now = time.time()
            if (now - start) >= self.time_limit:
                print(">>> Job killed due to time limit")
                break
        self.results = results
        self.reference = reference
        return results


    def validate(self, graphs=None, all_results=None, all_truth=None):
        """
        Validatate results.
        """
        if all_results == None:
            all_results = self.results
            if self.results == None:
                print("No predictions made yet!")
                return
        if graphs == None:
            graphs = self.graphs

        num_correct = 0
        total = 0
        for i in range(len(all_results)):
            result = all_results[i]
            if all_truth == None:
                graph = graphs[i]
                truth = graph["truth"]
            else:
                truth = all_truth[i]
            assert len(result) == len(truth), "mismatch of length between pred and truth"
            for i in range(len(result)):
                if result[i] == truth[i]:
                    num_correct += 1
                total += 1
        return num_correct / total
