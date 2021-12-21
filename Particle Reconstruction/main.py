# Copyright 2019 D-Wave Systems, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# ------- Import necessary packages -------
from matplotlib import pyplot as plt
import networkx as nx
import argparse
import sys
import os
import importlib
import itertools
import time
import random

import dataset
import annealing
import utils

# ------- Add terminal commands -------
if __name__ == "__main__":
    config_name = sys.argv[1]
    config = importlib.import_module(f"src.configs.{config_name}")
    if len(sys.argv) > 2:
        save_fig = "-s" in sys.argv
    else:
        save_fig = False

if config.method == "annealing":
    solver = annealing.max_cut_solver
elif config.method == "qaoa":
    raise NotImplementedError

inname = config.input_dir
try:
    outname = config.output_dir
except:
    outname = "outputs"
cwd = os.getcwd()
input_file = os.path.join(cwd, inname)
input_name = str(input_file)
output_dir = os.path.join(cwd, outname)
if os.path.exists(output_dir):
    print(f">>> Use existing output directory\n>>> Path: {output_dir}")
else:
    os.makedirs(output_dir, exist_ok=True)
    print(f">>> Output directory created\n>>> Path: {output_dir}")

model_name = config.model_name
model_file = importlib.import_module(f"src.models.{model_name}")
model_class = model_file.Model

num_evts = config.num_evts

# ------- Load dataset -------
assert os.path.exists(input_file), f"{input_file} does not exist!"
root = dataset._ROOT()
data = root.read(input_name, nentries=num_evts*1000)
model = model_class(data, num_evts, output_dir, save_fig)

stamp1 = time.time()
results = model.get_results(solver)
auc = model.validate()
final_result = [{"Jet Index": list(range(len(results))) + ["Accuracy"], 
                 "Is Tau": results + [auc]}]
print(f">>> Accuracy: {auc:.4f}")

result_name = f"Result for {config_name}.csv"
result_file = os.path.join(output_dir, result_name)
csv = dataset._CSV()
csv.write(final_result, result_file)

stamp2 = time.time()
print(f">>> Job finished in {utils.time_lasted(stamp2 - stamp1)}")