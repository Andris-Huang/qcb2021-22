import pandas as pd
import time
import utils
import itertools

class Dataset:
    """
    Class for different structures of dataset.
    """
    def __init__(self, name):
        self.name = name
    
    def read(self, filename):
        """
        Read data from a given file under filename.
        """
        raise NotImplementedError

    def write(self, content, filename):
        """
        Write content into a file under filename. Create a new file if current file does not exist.
        """
        raise NotImplementedError

    def make_graph(self, data):
        """
        Convert the data read into graphs
        """
        raise NotImplementedError


class _CSV(Dataset):
    """
    Class for .csv and/or excel files.
    """
    def __init__(self):
        super().__init__(name="CSV")
        
    def read(self, filename):
        """
        Input:
            filenamefilename: input file path
        Return:
            pandas DataFrame
        """
        return pd.read_csv(filename)

    def write(self, content, filename):
        """
        Input:
            content: list of dictonary-like object
            filename: file path
        Return:
            None
        """
        now = time.time()
        df = pd.concat([pd.DataFrame(c) for c in content], ignore_index=False, axis=1)
        df.to_csv(filename, index=False)
        cur = time.time()
        delta_t = utils.time_lasted(cur - now)
        print(f">>> Successfully finished writing to {filename} in {delta_t}")

    def make_graph(self, data, nodes_name="Courses", edge_weights="Conflicts", debug=False):

        # Nodes
        nodes = [d for d in data[nodes_name] if type(d)==str]
        if debug:
            print(nodes)
        n_nodes = len(nodes)

        # Edges
        weights = [d for d in data[edge_weights] if type(d)==int or type(d)==float]
        edges = list(itertools.combinations(range(n_nodes), 2))
        n_edges = len(edges)
        assert len(weights) == n_edges, "Number of Edge Weights Is Wrong"
        edge_list = [(edges[i][0], edges[i][1], weights[i]) for i in range(n_edges)]
        edge_labels = {}
        for i in range(len(edges)):
            key = edges[i]
            edge_labels[key] = weights[i]

        graph = {
            "n_node": n_nodes,
            "n_edge": n_edges,
            "nodes": nodes,
            "edges": edge_list,
            "edge_labels": edge_labels
            }
        return graph


class _ROOT(Dataset):
    """
    Class for .root files
    """
    def __init__(self):
        import ROOT
        super().__init__(name="ROOT")
        self.tree_name = "output"
    
    def _num_evts(self, filename):
        import ROOT
        chain = ROOT.TChain(self.tree_name, self.tree_name) # pylint: disable=maybe-no-member
        chain.Add(filename)
        n_entries = chain.GetEntries()
        return n_entries

    def read(self, filename, start_entry=0, nentries=float('inf')):
        import ROOT
        nentries = min(self._num_evts(filename), nentries)
        chain = ROOT.TChain(self.tree_name, self.tree_name) # pylint: disable=maybe-no-member
        chain.Add(filename)
        tot_entries = chain.GetEntries()
        nentries = nentries if (start_entry + nentries) <= tot_entries\
            else tot_entries - start_entry

        for ientry in range(nentries):
            chain.GetEntry(ientry + start_entry)
            yield chain


class _TXT(Dataset):
    """
    Class for .txt files
    """
    def __init__(self):
        super().__init__(name="TXT")

    def read(self, filename, start_entry=0, nentries=float('inf')):
        counter = 0
        with open(filename, 'r') as f:
            for line in f:
                if counter < start_entry:
                    pass
                elif counter >= nentries:
                    break
                yield [float(x) for x in line.split()]
                counter += 1
    