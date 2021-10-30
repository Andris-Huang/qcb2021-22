# QCB Project Fall 2021

## Setup Instructions
* Firstly, create a new conda environment and python kernel named "qcb" (but you can name it however you want). To do so, paste the following commands into your terminal:
```
module load python
conda create -n qcb python=3.8 ipykernel
source $(which conda | sed -e s#bin/conda#bin/activate#)  qcb
python -m ipykernel install --user --name qcb --display-name QCB
```
* Setup the kernel, run
```
conda env list
```
* Copy the path in the line next to the name "qcb", it should look like something like this:
```
/opt/conda/envs/qcb
```
* cd into the directory you just copied, do something like this
```
cd /opt/conda/envs/qcb
```
* Run the following command:
```
vim setup.sh
```
* You should see a file editing interface has shown up in the terminal. Now press <b> i </b> on the keyboard, <b> right click </b> and paste the following codes:
```
#!/bin/bash
module load python
source $(which conda | sed -e s#bin/conda#bin/activate#)  qcb
python -m ipykernel_launcher $@
```
* Now press <b> esc </b> on the keyboard and type <b> :wq </b> and press <b> enter </b>, you should now be back to the terminal. To check if you had the correct setup.sh file, run <b> cat setup.sh </b>, and you should see the codes you just pasted. If not, there are some issues and you should repeat the procedures.
* Run code below, the path below should be the one you copied earlier, plus <b> setup.sh </b> at the end
```
chmod +x /opt/conda/envs/qcb/setup.sh
```
* Run the following line and copy the output path
```
readlink -f setup.sh
```
* Run
```
vim kernel.json
```
* Delete everything in there and paste the following, the path right after "argv" is the path you just copied, everything else should be the same as the following:
```
{
 "argv": [
  "/opt/conda/envs/qcb/setup.sh",
  "-f",
  "{connection_file}"
 ],
 "display_name": "QCB",
 "language": "python"
}
```
* Lastly, install the libraries needed. cd into the github repo directory, and run
```
conda activate qcb
sh setup.sh
```
* Keep pressing enter if anything is prompted. After everything finished running, you should be all set!

## Resource Links
* Tracking Project Progress: https://docs.google.com/document/d/1MkPjx7Hh4-al4JboBponMp8Ufa1XRJyrJKwsgfcESzI/edit?usp=sharing
* Berkeley JupyterHub: https://datahub.berkeley.edu/
* GitHub Workflow: https://guides.github.com/introduction/git-handbook/#repository
* CS 61B Git Summary: https://inst.eecs.berkeley.edu/~cs61b/fa21/docs/using-git.html
* Install Qiskit: https://qiskit.org/documentation/stable/0.24/install.html
* Install Cirq: https://quantumai.google/cirq/install
* Install Ocean: https://docs.ocean.dwavesys.com/en/latest/overview/install.html
