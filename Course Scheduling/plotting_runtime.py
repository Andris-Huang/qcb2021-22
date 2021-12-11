import dataset
import os
import itertools
import utils
from matplotlib import pyplot as plt
import numpy as np

outname = 'outputs'


csv = dataset.CSV()

file_name = 'Run Time.csv'
cwd = os.path.dirname(os.path.abspath(__file__))
output_dir = os.path.join(cwd, outname)
input_dir = os.path.join(output_dir, file_name)
data = csv.read(input_dir)



n_node = list(data["Number of Nodes"])
run_time = list(data["Time (s)"])
log_name = "Run Time.png"
log_img = os.path.join(output_dir, log_name)

file_name = 'Run Time 2.csv'
output_dir = os.path.join(cwd, outname)
input_dir = os.path.join(output_dir, file_name)
data = csv.read(input_dir)

n_node.extend(list(data["Number of Nodes"]))
run_time.extend(list(data["Time (s)"]))

file_name = 'Run Time 3.csv'
output_dir = os.path.join(cwd, outname)
input_dir = os.path.join(output_dir, file_name)
data = csv.read(input_dir)

n_node.extend(list(data["Number of Nodes"]))
run_time.extend(list(data["Time (s)"]))

file_name = 'Run Time 4.csv'
output_dir = os.path.join(cwd, outname)
input_dir = os.path.join(output_dir, file_name)
data = csv.read(input_dir)

n_node.extend(list(data["Number of Nodes"]))
run_time.extend(list(data["Time (s)"]))

x = np.linspace(0, max(n_node), max(n_node))
y1 = x ** (1/2)
y2 = max(run_time)/2**(max(n_node)/20)*(2**(x/20))
y3 = x
y4 = max(run_time)/(max(n_node)**2) * (x**2)
ax = plt.subplots(figsize=(6, 6))[1]
ax.scatter(n_node, run_time)
ax.plot(x, y1, color="red", label="y=x^(1/2)")
ax.plot(x, y3, color="green", label="y=x")
ax.plot(x, y2, color="orange", label="y=a2^(x/20)")
ax.plot(x, y4, color="purple", label="y=ax^2")

ax.set_title("Run Time vs Graph Size")
ax.set_ylabel("Time (s)", fontsize=12)
ax.set_xlabel("Number of Nodes", fontsize=12)
ax.legend()
plt.tight_layout()
plt.show()
plt.savefig(log_img, bbox_inches='tight')