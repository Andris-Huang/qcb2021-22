# Course Scheduling Using Max-Cut
## Background
The Max-cut problem is a type of graph problem that focuses on partition and grouping. A simple undirected graph can be defined as G=(V,E), where V is the set of all vertices and E is the set of all edges. Each node x has an assigned value and each edge e carries a numerical edge weight w given by the context of a specific problem. The task for a Max-cut problem is to use one "cut" that disconnects an arbitrary number of edges and partitions the graph into two disjoint subsets S0 and S1, such that the sum of edges for the disconnected edges is maximized. Many real-life situations can be modeled as a Max-cut problem, and thus its solution is useful for many fields, including physics, chemistry, finance, etc. Given the recent development in quantum computing, there have been many approaches to find or approximate the solutions to Max-cut problems, including quantum annealing and QAOA.

## Model
The goal of this project is to create a course scheduling system to allocate the time blocks for courses in a way that minimizes the time conflicts, so that the most number of students can attend the courses they desire with the least conflicts. As a result, we encode the courses as the nodes of the graphs and constructs a fully-connected graph. We then assign the number of students taking the two courses concurrently as the weight of the edge that connects the corresponding two courses. After that, we perform the algorithm that solves the Max-cut problem (Max-cut solver) two separate the graph into two groups, then recursively apply it to the subgroups to separate them into multiple groups, until the number of courses in each subgroup is less than a threshold value given by the user.

## Results
In this project, we randomly generated 150 courses from 6 departments, and assigned the number of students taking any two courses concurrently to be an integer in range [1, 400]. We first constructed a fully-connected graph with 150 nodes then perform the algorithm described in models and separated the courses into 21 time blocks with less than 10 courses per block using quantum annealing, running on D-Wave's quantum annealer. We repeated this procedure on the same graph multiple times to collect more data points, and our best run reduced the total conflict by 95.58%.

## Resource Links
* Max-Cut and Traveling Salesman Problem — Qiskit 0.24.0 documentation (https://qiskit.org/documentation/tutorials/optimization/6_examples_max_cut_and_tsp.html)
* QAOA: Max-Cut | Cirq (https://quantumai.google/cirq/tutorials/qaoa)
* dwave-examples/graph-partitioning: Split a graph into two groups (https://github.com/dwave-examples/graph-partitioning)
* Efficient encoding of the weighted MAX k-CUT on a quantum computer using QAOA (https://arxiv.org/pdf/2009.01095.pdf)
