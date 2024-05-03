import os
import subprocess
import sys
import glob
import re


def findFileIndex(file, files):
    idx = 0
    for f in files:
        if f == file:
            return idx
        idx += 1
    return -1


def findDepencencies(vhdlFile, adjListOut, adjListIn, fileIdx):
    try:
        with open(vhdlFile, 'r') as file:
            for line in file:
                regexRule = r'[^-]component \w+ is'
                match = re.findall(regexRule, line, flags=re.IGNORECASE)
                if match:
                    component = line.split()[1]
                    dependency = component + ".vhd"
                    adjListOut[findFileIndex(dependency, vhdlFiles)].append(fileIdx)
                    adjListIn[fileIdx].append(findFileIndex(dependency, vhdlFiles))

    except FileNotFoundError:
        print(f"VHDL file {vhdlFile} not found")
    except Exception as e:
        print("Error reading VHDL file", e)


def topologicalSort(adjListOut, adjListIn):
    orderOfCompilation = []
    startNodes = []
    for i in range(len(adjListIn)):
        if len(adjListIn[i]) == 0:
            startNodes.append(i)

    while len(startNodes) > 0:
            n = startNodes.pop(0)
            orderOfCompilation.append(n)
            while len(adjListOut[n]) > 0:
                m = adjListOut[n][0]
                adjListOut[n].remove(m)
                adjListIn[m].remove(n)
                if len(adjListIn[m]) == 0:
                    startNodes.append(m)

    return orderOfCompilation


# TODO: test if path id directory and not file
projectPath = sys.argv[1]
if projectPath == ".":
    projectPath = subprocess.check_output("pwd")
    projectPath = projectPath.decode("utf-8")
    projectPath = projectPath.replace("\n", "")
if projectPath[0] == "~":
    projectPath = os.path.expanduser(projectPath)
if projectPath[-1] != "/":
    projectPath += "/"

os.chdir(projectPath)

# TODO: not add unwanted vhdl files
vhdlFiles = glob.glob("**/*.vhd")
vhdlFiles += glob.glob("*.vhd")


# Create the empty adjacency lists
adjacencyListOutgoing = []
adjacencyListIncoming = []
for i in range(len(vhdlFiles)):
    adjacencyListOutgoing.append([])
    adjacencyListIncoming.append([])

fileIdx = 0
for vhdlFile in vhdlFiles:
    findDepencencies(vhdlFile, adjacencyListOutgoing, adjacencyListIncoming, fileIdx)
    fileIdx += 1

print(adjacencyListOutgoing)
print(adjacencyListIncoming)
orderOfCompilation = topologicalSort(adjacencyListOutgoing, adjacencyListIncoming)
print(vhdlFiles)

for i in orderOfCompilation:
    os.system(f"ghdl -a {vhdlFiles[i]}")
    component = vhdlFiles[i].replace(".vhd", "")
    component = component.split("/")[-1]
    os.system(f"ghdl -e {component}")
