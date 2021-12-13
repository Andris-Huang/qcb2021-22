import dataset
import os
import itertools
import utils
from matplotlib import pyplot as plt
import numpy as np
import sys


if __name__ == "__main__":
    n_node, run_time = [], []
    csv = dataset.CSV()
    fileID = sys.argv[1:]
    outname = 'outputs'

    csv = dataset.CSV()

    cwd = os.getcwd()
    output_dir = os.path.join(cwd, outname)
    log_name = "Run Time.png"
    log_img = os.path.join(output_dir, log_name)

    for i in fileID:
        file_name = f'Run Time {i}.csv'
        input_dir = os.path.join(output_dir, file_name)
        data = csv.read(input_dir)

        n_node.extend(list(data["Number of Nodes"]))
        run_time.extend(list(data["Time (s)"]))


    x = np.linspace(0, max(n_node), max(n_node))
    y = max(run_time)/2**(max(n_node)/20)*(2**(x/20))
    ax = plt.subplots(figsize=(6, 6))[1]
    ax.scatter(n_node, run_time)
    ax.plot(x, y, color="orange", label="O(exp(x))")

    ax.set_title("Run Time vs Graph Size")
    ax.set_ylabel("Time (s)", fontsize=12)
    ax.set_xlabel("Number of Nodes", fontsize=12)
    ax.legend()
    plt.tight_layout()
    plt.show()
    plt.savefig(log_img, bbox_inches='tight')