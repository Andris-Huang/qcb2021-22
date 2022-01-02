# Particle Reconstruction through Quantum Annealing
## Background
In high energy physics, a meaningful study is to create an algorithm that classifies the type of jets. A jet is a cluster of energy created from a particle after its decay, likely resulting from a collision event. The detector would collect information about the jet to infer what particle(s) was involved in the collision and decay process. Current algorithms used for jet classification include decision trees, recurrent neural networks, and graph neural networks.

## Model
We established the nodes as various jets in one event, each contains a list of variables and their values. We then created a fully-connected graph with the edges between two nodes being the “mean difference” between the values of the node variables. This “mean difference” is determined by using inner product between the attributes of the nodes. In the ideal situation, the “mean difference” between two different types of jets will be large, whereas the difference between two jets of the same kind will be trivial. We then apply the max-cut solver to separate the nodes into two groups: IS a desired jet or is NOT a desired jet.

## Results
* Config 1: Classification based on di-tau mass using quantum annealing
    * We obtained an accuracy of 54.29% for 300 gamma to di-tau decay events finished in 7.97 minutes. We also obtained an accuracy of 57.17% for 300 Z-boson to di-tau events finished in 8.57 minutes.
* Config 2: Clustering based on four vectors using quantum annealing
    * We obtained an accuracy of 50.26% for 22 W' to WZ decay events with less than 80 nodes per graph finished in 30.29 minutes. Observed that classical brute-force solution does not work on this task.

## How to Run
* Install the necessary packages and libraries by running the setup.sh file in the parent directory qcb2021-22
* Run main.py in command line with the name for the configuration

## References
* Track clustering with a quantum annealer for primary vertex reconstruction at hadron colliders (https://arxiv.org/abs/1903.08879)
* Solving a Higgs optimization problem with quantum annealing for machine learning (https://www.nature.com/articles/nature24047)
* Multilevel Quantum Annealing For Graph Partitioning (https://www.dwavesys.com/media/twphvuuk/13_tues_pm_clemson_0.pdf)
* Graph Partitioning using Quantum Annealing on the D-Wave System (https://arxiv.org/abs/1705.03082)
* Potential Dataset: Top-quark (https://zenodo.org/record/2603256#.YXTC-nrMKUl); Lorentz Boosted Bosons (https://zenodo.org/record/3981290#.Yc18vROZNhG)
