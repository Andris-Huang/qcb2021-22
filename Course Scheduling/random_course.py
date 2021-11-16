import os
import dataset
import utils
import argparse
import itertools
import random

parser = argparse.ArgumentParser(description='Train GNN')
add_arg = parser.add_argument
add_arg("-t", "--target-dir", help="Target graph directory", default="inputs")
add_arg("-n", "--num-course", help="Number of random courses", default=150)
args = parser.parse_args()

outname = args.target_dir
n_course = args.num_course

cwd = os.path.dirname(os.path.abspath(__file__))
output_dir = os.path.join(cwd, outname)

if os.path.exists(output_dir):
    print(f">>> Use existing output directory\n>>> Path: {output_dir}")
else:
    os.makedirs(output_dir, exist_ok=True)
    print(f">>> Output directory created\n>>> Path: {output_dir}")

filename = "Random Course.csv"
csv = dataset.CSV()

department = ["CS", "PHYS", "MATH", "CHEM", "DS", "EE"]
course_num = list(range(10, 200))

courses = []
for n in range(n_course):
    courses.append(f"{department[n % len(department)]} {course_num[n]}")

edges = list(itertools.combinations(range(n_course), 2))
conflicts = [random.randint(1,400) for _ in edges]
data = [{"Courses": courses}, {"Conflicts": conflicts}]

out_file = os.path.join(output_dir, filename)
csv.write(data, out_file)