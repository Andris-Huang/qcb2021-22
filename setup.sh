#!/bin/bash
pip install qiskit
pip install qiskit[visualization]
pip install numpy
pip install scipy
pip install matplotlib
pip install pandas
pip install sklearn
pip install networkx
python -m pip install cirq
pip install dwave-ocean-sdk
dwave setup --all
dwave install -a