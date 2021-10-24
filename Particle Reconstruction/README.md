# Particle Reconstruction
## Project Description
### Overview
Program QML model that takes in information about a particle collision/decay event (Energy, momentum, etc.) and outputs attributes about the particle(s) in the interaction (mass, charge, spin, etc.) 
### Group Size
3-5 people, at least one semester would be needed
### Objectives
* Understand the basic particle reconstruction algorithms existed in the field
* Use the open-source dataset published by Lawrence Berkeley Lab and process them into desired forms
* Try implement a Quantum Machine Learning Model(s) based on current RNN or GNN model, or other methods based on max-cut and/or decision tree
* Observe the performance of the QML model and discuss potential improvements
### Current Idea
* Task: Jet classification
* Background: In high energy physics, a meaningful study is to create an algorithm that classifies the type of jets. A jet is a cluster of energy created from a particle after its decay, likely resulting from a collision event. The detector would collect information about the jet to infer what particle(s) was involved in the collision and decay process. Current algorithms used for jet classification include decision trees, recurrent neural networks, and graph neural networks.
* Method: one possible idea for our group is to apply the max-cut algorithm on jets. We could establish the nodes as various jets in one event, each contains a list of variables and their values. The edges between two nodes will be the “mean difference” between the values of the node variables. This “mean difference” is still undetermined. However, in the ideal situation, the “mean difference” between two different types of jets will be large, whereas the difference between two jets of the same kind will be trivial. As a result, we could use this algorithm as a binary decision method to classify a group of jets into two groups: IS or IS NOT from a certain type of particle. We could also use max-cut along with the decision tree, which was studied in past works but has not been used in high energy physics. Other machine learning algorithms could also be applied if desired.
### Challenges
* The performance of QML is unknown, could be very terrible
* The implementation could be too advanced
* Some background of particle physics is needed

## Resource Links
* Track clustering with a quantum annealer for primary vertex reconstruction at hadron colliders (https://arxiv.org/abs/1903.08879)
* Solving a Higgs optimization problem with quantum annealing for machine learning (https://www.nature.com/articles/nature24047)
* Multilevel Quantum Annealing For Graph Partitioning (https://www.dwavesys.com/media/twphvuuk/13_tues_pm_clemson_0.pdf)
* Graph Partitioning using Quantum Annealing on the D-Wave System (https://arxiv.org/abs/1705.03082)