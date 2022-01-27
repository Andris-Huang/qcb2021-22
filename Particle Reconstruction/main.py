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
import utils

# ------- Add terminal commands -------
if __name__ == "__main__":
    indent = " " * 4
    helper = f">>> Possible commands:" \
           + f"\n{indent}-s: save graphs" \
           + f"\n{indent}-d: do not save result" \
           + f"\n{indent}--debug: use debug mode" \
           + f"\n{indent}--heff: hide efficiency for solver"
    if len(sys.argv) < 2:
        print(">>> A configuration is needed!")
        print(">>> Use --help for direction to commands.")
        exit()
    if "--help" in sys.argv:
        print(helper)
        exit()
    config_name = sys.argv[1]
    config = importlib.import_module(f"src.configs.{config_name}")
    save_fig = "-s" in sys.argv
    save_result = not "-d" in sys.argv
    debug = "--debug" in sys.argv
    display_efficiency = not "--heff" in sys.argv and config.method != "clustering"


if debug:
    save_fig = True
    save_result = False

method = importlib.import_module(f"src.methods.{config.method}")
solver = method.solver

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

model_names = config.model_name
model_name = model_names if isinstance(model_names, str) else model_names[0]
print(f">>> Model: {model_names}; Solver: {config.method}")
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
results = model.get_results(solver, display_efficiency=display_efficiency)

if debug:
    print(f"***Results: {results}***")
    truth = model.graphs[0]["truth"]
    print(f"***Truth: {truth}***")

acc = model.validate()
if display_efficiency:
    eff = model.validate(all_truth=model.reference)
    max_eff = model.validate(all_results=model.reference, all_truth=model.truth)
else:
    eff, max_eff = "N/A", "N/A"
stamp2 = time.time()

dt = utils.time_lasted(stamp2 - stamp1)
final_result = [{"Event Index": list(range(len(results))) \
                 + ["Accuracy", "Time", "Efficiency", "Max Possible Accuracy", "Event Ratio"], 
                 "Is Tagged": results + [acc, dt, eff, max_eff, model.event_ratio]},
                {"Reference": model.reference},
                {"Truth": model.truth}]
print(f">>> Accuracy: {acc:.4f}")

if save_result:
    result_name = f"Result for {config_name}.csv"
    result_file = os.path.join(output_dir, result_name)
    csv = dataset._CSV()
    csv.write(final_result, result_file)

print(f">>> Job finished in {dt}")