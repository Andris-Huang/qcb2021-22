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
import brute_solver
import utils

# ------- Add terminal commands -------
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(">>> A configuration is needed!")
        exit()
    config_name = sys.argv[1]
    config = importlib.import_module(f"src.configs.{config_name}")
    if len(sys.argv) > 2:
        save_fig = "-s" in sys.argv
        save_result = not "-d" in sys.argv
        debug = "--debug" in sys.argv
    else:
        save_fig = False
        save_result = True
        debug = False

if debug:
    save_fig = True

if config.method == "annealing":
    solver = annealing.max_cut_solver
elif config.method == "qaoa":
    raise NotImplementedError
elif config.method == "brute":
    solver = brute_solver.brute_solver

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
    print(f">>> Use existing output directory\n>>> Output Path: {output_dir}")
else:
    os.makedirs(output_dir, exist_ok=True)
    print(f">>> Output directory created\n>>> Output Path: {output_dir}")

model_name = config.model_name
model_file = importlib.import_module(f"src.models.{model_name}")
model_class = model_file.Model

num_evts = config.num_evts

# ------- Load dataset -------
assert os.path.exists(input_file), f"{input_file} does not exist!"
editor = getattr(dataset, f"_{config.file_type}")()
data = editor.read(input_name)

if debug:
    print("***Finished reading data***")
    num_evts = 1

model = model_class(data, num_evts, output_dir, save_fig, config=config, debug=debug)

stamp1 = time.time()
results = model.get_results(solver)

if debug:
    print(f"Results: {results}")

acc = model.validate()
stamp2 = time.time()

dt = utils.time_lasted(stamp2 - stamp1)
final_result = [{"Event Index": list(range(len(results))) + ["Accuracy", "Time"], 
                 "Is Tagged": results + [acc, dt]}]
print(f">>> Accuracy: {acc:.4f}")

if save_result:
    result_name = f"Result for {config_name}.csv"
    result_file = os.path.join(output_dir, result_name)
    csv = dataset._CSV()
    csv.write(final_result, result_file)

print(f">>> Job finished in {dt}")