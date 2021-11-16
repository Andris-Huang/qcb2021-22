import dataset
import os
import itertools
import utils
from matplotlib import pyplot as plt

outname = 'outputs'


csv = dataset.CSV()

file_name = 'Run Time.csv'
cwd = os.path.dirname(os.path.abspath(__file__))
output_dir = os.path.join(cwd, outname)
input_dir = os.path.join(output_dir, file_name)
data = csv.read(input_dir)

n_node = data["Number of Nodes"]
run_time = data["Time (s)"]
log_name = "Run Time.png"
log_img = os.path.join(output_dir, log_name)


ax = plt.subplots(figsize=(6, 6))[1]
ax.scatter(n_node, run_time)
ax.set_title("Run Time vs Graph Size")
ax.set_ylabel("Time (s)", fontsize=12)
ax.set_xlabel("Number of Nodes", fontsize=12)
plt.tight_layout()
plt.show()
plt.savefig(log_img, bbox_inches='tight')