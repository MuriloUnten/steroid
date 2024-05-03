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


# TODO: test if path id directory and not file
projectPath = sys.argv[1]
if projectPath == ".":
    projectPath = subprocess.check_output("pwd")
    projectPath = projectPath.decode("utf-8")
    projectPath = projectPath.replace("\n", "")
print(projectPath)
if projectPath[0] == "~":
    projectPath = os.path.expanduser(projectPath)
if projectPath[-1] != "/":
    projectPath += "/"
print(projectPath)

# TODO: not add unwanted vhdl files
vhdlFiles = glob.glob(projectPath + "*.vhd")

adjacencyList = []
adjacencyListIncoming = []
for i in range(len(vhdlFiles)):
    adjacencyList.append([])
    adjacencyListIncoming.append([])

fileIdx = 0
print(vhdlFiles)
for vhdlFile in vhdlFiles:
    try:
        with open(vhdlFile, 'r') as file:
            for line in file:
                regexRule = r'[^-]component \w+ is'
                match = re.findall(regexRule, line, flags=re.IGNORECASE)
                if match:
                    component = line.split()[1]
                    dependency = projectPath + component + ".vhd"
                    adjacencyList[findFileIndex(dependency, vhdlFiles)].append(fileIdx)
                    adjacencyListIncoming[fileIdx].append(findFileIndex(dependency, vhdlFiles))

    except FileNotFoundError:
        print(f"VHDL file {vhdlFile} not found")
    except Exception as e:
        print("Error reading VHDL file", e)

    fileIdx += 1

# Topological Sorting
# TODO: Break into function
orderOfCompilation = []
startNodes = []
for i in range(len(adjacencyListIncoming)):
    if len(adjacencyListIncoming[i]) == 0:
        startNodes.append(i)

while len(startNodes) > 0:
        n = startNodes.pop(0)
        orderOfCompilation.append(n)
        while len(adjacencyList[n]) > 0:
            m = adjacencyList[n][0]
            adjacencyList[n].remove(m)
            adjacencyListIncoming[m].remove(n)
            if len(adjacencyListIncoming[m]) == 0:
                startNodes.append(m)

print(orderOfCompilation)
        

os.system(f"cd {projectPath}")
for i in orderOfCompilation:
    os.system(f"ghdl -a {vhdlFiles[i]}")
    os.system(f"ghdl -e {vhdlFiles[i]}")
