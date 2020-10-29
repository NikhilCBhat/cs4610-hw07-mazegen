"""
Adapted from:
https://code.sololearn.com/ckL449yet03G/#py

Refactored code to make it easier to understand,
easier to use, and better suited for this assignment
"""

import random


## --  Constants -- ## 
SIZE = 5
SEED = None
STYLES = ("A")

DIR_A = (1, 0, -1)
DIR_B = (1, -1, 0)
DIR_C = (0, 1, -1)
DIR_D = (-1, 0, 1)
DIR_E = (-1, 1, 0)
DIR_F = (0, -1, 1)

DIRS = (DIR_A, DIR_B, DIR_C, DIR_D, DIR_E, DIR_F)
TRANSPARENT = ""

START = (SIZE, 0, -SIZE)
END = (-SIZE, 0, SIZE)

V1_A = (2, 0)
V2_A = (1, 2)

## --  Graph Class -- ## 

class Graph:

  def __init__(self):
    self.parentMap = {}

  def getParent(self, node):
    return self.parentMap.get(node, node)

  def setParent(self, node, parent):
    self.parentMap[node] = parent

  def find(self, node):
    if self.getParent(node) == node:
      return node
    else:
      result = self.find(self.getParent(node))
      self.setParent(node, result)
      return result
      
  def componentunion(self, nodeX, nodeY):
    roots = [self.find(nodeX), self.find(nodeY)]
    if roots[0] != roots[1]:
      random.shuffle(roots)
      self.setParent(roots[0], roots[1])

  def isAlreadyConnected(self, nodeX, nodeY):
    return self.find(nodeX) == self.find(nodeY)


## --  Drawing Functions -- ## 

def spaceToTransparent(char):
  return TRANSPARENT if char == " " else char

def createEmpty():
  return lambda coord: TRANSPARENT

def create(string):
  lines = string.split("\n")
  def result(coord):
    x, y = coord
    if x >= 0  and x < len(lines):
      if y >= 0 and y < len(lines[x]):
        return spaceToTransparent(lines[x][y])
    return TRANSPARENT  
  return result

DOORS_STYLE_A = {
  DIR_A: create("\n\n _"),
  DIR_B: create("\n\n\\"),
  DIR_C: create("\n\n  /"),
  DIR_D: create(" _"),
  DIR_E: create("\n  \\"),
  DIR_F: create("\n/")  
}

def translate(stringArt, vect):
  return lambda coord: stringArt((coord[0] - vect[0], coord[1] - vect[1]))

def saunion(stringArts):
  def result(coord):
    x, y = coord
    for art in stringArts:
      if art(coord) != TRANSPARENT:
        return art(coord)
    return TRANSPARENT
  return result

def resolveChar(char):
  return  " " if char == TRANSPARENT else char

def printArt(stringArt, dimension):
  sizeX, sizeY = dimension
  lines = []
  for i in range(sizeX):
    line = "".join([resolveChar(stringArt((i, j))) for j in range(sizeY)])
    print(line)
    lines.append(line)
  return lines

def getMazeArt(nodes, edges, pathNodes):
    def getNodeArt(node):
        translation = nodeToCoordStyleA(node)
        hexaProvider = hexProviderA
        openDoors = getOpenDoorsFrom(node, edges)
        hexaArt = hexaProvider(openDoors, node in pathNodes)
        return translate(hexaArt, translation)
    return saunion([getNodeArt(node) for node in nodes])

def printMaze(nodes, edges, size, showSolution = False):
    pathNodes = set()
    mazeArt = translate(getMazeArt(nodes, edges, pathNodes), (2 * size, 2 * size))
    return printArt(mazeArt, (4 * size + 3, 4 * size + 3))

def hexProviderA(openDoors, isInPath = False):
  doors = [door for direction, door in DOORS_STYLE_A.items() if direction not in openDoors]
  return saunion(doors)

## --  Maze Generation -- ## 
def isInside(node, size):
    x, y, z = node
    return max((abs(x), abs(y), abs(z))) <= size

def addVector(vec1, vec2):
    return tuple(map(lambda x, y: x + y, vec1, vec2))

def getNeighbors(node):
   return tuple(map(lambda x: addVector(node, x), DIRS))
    
def getNodes(size):
    result = []
    for i in range(-size, size + 1):
        for j in range(-size, size + 1):
            if abs(i + j) <= size:
                result.append(tuple([i, j, -(i+j)]))
    return tuple(result)

def createEdge(node1, node2):
    if node1 < node2:
        return (node1, node2)
    else:
        return (node2, node1)

def getEdges(nodes, size):
    result = list()
    for node in nodes:
        for neighbor in getNeighbors(node):
            if isInside(neighbor, size):
                result.append(createEdge(node, neighbor))
    return result

def generateMazeEdges(edgeList):
  mazeEdges = set()
  g = Graph()
  for edge in edgeList:
    node1, node2 = edge
    if not g.isAlreadyConnected(node1, node2):
      g.componentunion(node1, node2)
      mazeEdges |= {edge}
  return mazeEdges

def shuffle(edgeList, seed = None):
    if seed == None:
        seed = random.randint(0, 1000)
    random.seed(seed)
    random.shuffle(edgeList)

def nodeToCoordStyleA(node):
    x, y, z = node
    return (x * V1_A[0] + y * V2_A[0], x * V1_A[1] + y * V2_A[1])

def getOpenDoorsFrom(node, edges):
  nodeEdges = set(filter(lambda edge: node in edge, edges))
  return {direction for direction in DIRS if createEdge(node, addVector(node, direction)) in nodeEdges}

def addEdgeToDict(edge, dictionary):
  start, end = edge
  if (start in dictionary):
    dictionary[start].append(end)
  else:
    dictionary[start] = [end]

def getNeighborsDict(edges):
  result = {}
  for edge in edges:
    addEdgeToDict(edge, result)
    addEdgeToDict(edge[::-1], result)
  return result

def backtracePath(previousFieldDict, start):
  current = start
  result = []
  while (current != previousFieldDict[current]):
    result.append(current)
    current = previousFieldDict[current]
  result.append(current)
  return result

def getPath(edges, startNode, endNode):
    parentDict = {startNode: startNode}
    neighborsDict = getNeighborsDict(edges)
    queue = [startNode]
    while len(queue) > 0:
      current = queue.pop(0)
      neighbors = neighborsDict[current]

      unvisitedNeighbors = [neighbor for neighbor in neighbors if neighbor not in parentDict]
      unvisitedNeighborsDict = {neighbor: current for neighbor in unvisitedNeighbors}
      
      parentDict.update(unvisitedNeighborsDict)
      queue.extend(unvisitedNeighbors)

    if endNode in parentDict:
        return backtracePath(parentDict, endNode)
    else:
        return None

def generate_maze():
  nodes = getNodes(SIZE)
  edgeList = getEdges(nodes, SIZE)
  shuffle(edgeList, SEED)
  mazeEdges = generateMazeEdges(edgeList)

  return printMaze(nodes, mazeEdges, SIZE)
