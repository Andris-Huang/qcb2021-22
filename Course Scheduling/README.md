# Course Scheduling Using Max/Min Cut
## Project Description
### Overview
As a large public school, Cal students are always suffering from millions of course scheduling conflicts every year. Therefore, we could make a course scheduling algorithm by treating scheduling as a max-cut/min-cut problem. This project has two parts, each part can function independently. <br>
Max-cut is a decision problem type, in which we will be given a graph with nodes and edges that contains some weights, and we need to find a way to separate the nodes into two groups with one “cut” that maximizes the total weight. This type of problem can be solved using Grover’s search algorithm or the D-Wave quantum annealing method. Senior members in QCB have completed a project that utilizes max-cut on quarantine policies, which could be a good reference for this project.
### Group Size
* 2-3 people per part
* Can be a semester-long project with group size of 4-6 people, or a year-long project with 2-3 people
### Part 1
This part of the project is targeted at the campus staff who allocates the course times. We will construct graphs using different courses as the nodes and the number of students taking two classes at the same time as the edges/weights between the respective courses. Then, we will use quantum algorithms to separate the nodes into two groups that minimize the total weight, which represents the number of students having schedule conflicts. <br>
For instance, if we have 3 students A, B, C each taking courses as the following: <br>
A: C191, Math 275 <br>
B: C191, Physics 137A <br>
C: C191, Math 275 <br>
Then we will have a graph with the following attributes: <br>
Nodes (courses): C191, Math 275, Phys 137A <br>
Edges (fully connected between courses): (C191, M275), (M275, P137A), (P137A, C191) <br>
Weights on respective edges (number of students taking courses simultaneously): 2, 0, 1 <br>
Following this configuration, the max-cut algorithm should place a cut on the edges (C191, M275) & (P137A, C191) and separate the 3 courses into 2 groups as {M275, P137A}, {C191}. Courses in the same group can be offered at the same time, but courses from different groups should not. As a result, the staff could offer P137A and M275 at the same time on Tuesdays and C191 on Mondays, so that the scheduling conflicts should be minimized.
### Part 2
This part is targeted at students choosing courses for the semester. The current schedule planner on CalCentral only tells the users whether their chosen schedule has conflicts or not, but does not suggest a feasible course combination. Therefore, the goal of this part is to take a series of courses that a student wants to take as the input, and output the possible course combinations that minimize the schedule conflicts. <br>
To accomplish this goal, we will use the courses as nodes and the conflicts between them as edges and weights. We will use min-cut to minimize the total weight after separating the nodes into two groups. For instance, if a student wants to take 4 courses offered as the following: <br>
C191: Tu & Th 11am <br>
P137A: Tu 11am & Th 3pm <br>
M275: Tu & Th 3pm <br>
Then we will construct a graph as: <br>
Nodes: C191, P137A, M275 <br>
Edges: (C191, M275), (M275, P137A), (P137A, C191) <br>
Weights on respective edges (schedule conflicts): 0, 1, 1 <br>
Therefore, our algorithm should place a cut on  (M275, P137A) & (P137A, C191) and the nodes will be in two groups: {P137A}, {M275, C191}. So that the student will be recommended to only choose courses in one of the groups. <br>
### Objectives
* Understand Max-cut/Min-cut problems and quantum algorithms to solve these problems
* Implement and adjust the graph construction for the scheduling model
* Implement the min-cut algorithms that takes in the graphs constructed and output functioning and meaningful results
* Discuss the potential and possibility for future works (e.g. min k-cut)
### Challenges
* In reality, there are more time slots to be considered, so that separating the courses into merely 2 groups might not be useful
* The model has not been tested, so that we might encounter loopholes in our implementation
* The scalability of this algorithm is limited due to the constraints of quantum algorithms

## Resource Links
* Max-Cut and Traveling Salesman Problem — Qiskit 0.24.0 documentation (https://qiskit.org/documentation/tutorials/optimization/6_examples_max_cut_and_tsp.html)
* QAOA: Max-Cut | Cirq (https://quantumai.google/cirq/tutorials/qaoa)
* dwave-examples/graph-partitioning: Split a graph into two groups (https://github.com/dwave-examples/graph-partitioning)
* Efficient encoding of the weighted MAX k-CUT on a quantum computer using QAOA (https://arxiv.org/pdf/2009.01095.pdf)