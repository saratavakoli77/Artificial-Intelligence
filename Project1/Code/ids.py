from queue import Queue
from time import time

OBSTACLE_CH = '#'
AMBULANCE_CH = 'A'
PATIENT_CH = 'P'
SPACE_CH = ' '

class state:
    def __init__(self, ambulanceX, ambulanceY, newMap, parent):
        self.ambulanceX = ambulanceX
        self.ambulanceY = ambulanceY
        self.createHash(newMap)
        self.parent = parent
        self.setLevel()
        self.map = newMap
        self.depth = 0
        self.isGoalState = False
    def createHash(self, mapGraph):
        self.hashMap = ''
        for i in mapGraph:
            self.hashMap += ''.join(i)
            self.hashMap += '\n'
    def setLevel(self):
        if self.parent != None:
            self.level = self.parent.level + 1
        else:
            self.level = 0
    def isThisStateGoalState(self):
        thereIsPatient = False
        for i in self.map:
            if PATIENT_CH in i:
                thereIsPatient = True
                break
        self.isGoalState = not thereIsPatient

class mapActions:
    def __init__(self, fileName):
        f = open(fileName, "r")
        content = f.read()
        graph = content.splitlines()
        for i in range(len(graph)):
            graph[i] = list(graph[i])
        self.map = graph
        self.findAmbulance()
        self.height = len(graph)
        self.width = len(graph[0])
        self.numOfallExploredStates = 0
        self.numOfUniqueExploredStates = 0
        self.allReached = set()
    
    def changeMap(self, hashStr):
        graph = hashStr.splitlines()
        for i in range(len(graph)):
            graph[i] = list(graph[i])
        self.map = graph
        self.findAmbulance()

    def findAmbulance(self):
        for i in range(len(self.map)):
            for j in range(len(self.map[0])):
                if self.map[i][j] == AMBULANCE_CH:
                    self.ambulanceY = i
                    self.ambulanceX = j

    def moveRight(self):
        if self.ambulanceX < self.height - 3 and self.map[self.ambulanceY][self.ambulanceX+1] == PATIENT_CH and self.map[self.ambulanceY][self.ambulanceX+2].isnumeric():
            if int(self.map[self.ambulanceY][self.ambulanceX+2].isnumeric()) > 0:
                self.map[self.ambulanceY][self.ambulanceX] = SPACE_CH
                self.map[self.ambulanceY][self.ambulanceX+1] = AMBULANCE_CH
                self.map[self.ambulanceY][self.ambulanceX+2] = str(int(self.map[self.ambulanceY][self.ambulanceX+2])-1)
                self.ambulanceX+=1
                return True
        elif self.ambulanceX < self.width - 3 and self.map[self.ambulanceY][self.ambulanceX+1] == PATIENT_CH and self.map[self.ambulanceY][self.ambulanceX+2] == SPACE_CH:
            self.map[self.ambulanceY][self.ambulanceX] = SPACE_CH
            self.ambulanceX+=1
            self.map[self.ambulanceY][self.ambulanceX] = AMBULANCE_CH
            self.map[self.ambulanceY][self.ambulanceX+1] = PATIENT_CH
            return True
        elif self.ambulanceX < self.width - 2 and self.map[self.ambulanceY][self.ambulanceX+1] == SPACE_CH:
            self.map[self.ambulanceY][self.ambulanceX] = SPACE_CH
            self.ambulanceX+=1
            self.map[self.ambulanceY][self.ambulanceX] = AMBULANCE_CH
            return True
        else:
            return False

    def moveLeft(self):
        if self.ambulanceX > 2 and self.map[self.ambulanceY][self.ambulanceX-1] == PATIENT_CH and self.map[self.ambulanceY][self.ambulanceX-2].isnumeric():
            if int(self.map[self.ambulanceY][self.ambulanceX-2]) > 0:
                self.map[self.ambulanceY][self.ambulanceX] = SPACE_CH
                self.map[self.ambulanceY][self.ambulanceX-1] = AMBULANCE_CH
                self.map[self.ambulanceY][self.ambulanceX-2] = str(int(self.map[self.ambulanceY][self.ambulanceX-2])-1)
                self.ambulanceX-=1
                return True
        elif self.ambulanceX > 2 and self.map[self.ambulanceY][self.ambulanceX-1] == PATIENT_CH and self.map[self.ambulanceY][self.ambulanceX-2] == SPACE_CH:
            self.map[self.ambulanceY][self.ambulanceX] = SPACE_CH
            self.ambulanceX-=1
            self.map[self.ambulanceY][self.ambulanceX] = AMBULANCE_CH
            self.map[self.ambulanceY][self.ambulanceX-1] = PATIENT_CH
            return True
        elif self.ambulanceX > 1 and self.map[self.ambulanceY][self.ambulanceX-1] == SPACE_CH:
            self.map[self.ambulanceY][self.ambulanceX] = SPACE_CH
            self.ambulanceX-=1
            self.map[self.ambulanceY][self.ambulanceX] = AMBULANCE_CH
            return True
        else:
            return False

    def moveUp(self):
        if self.ambulanceY > 2 and self.map[self.ambulanceY-1][self.ambulanceX] == PATIENT_CH and self.map[self.ambulanceY-2][self.ambulanceX].isnumeric():
            if int(self.map[self.ambulanceY-2][self.ambulanceX]) > 0:
                self.map[self.ambulanceY][self.ambulanceX] = SPACE_CH
                self.map[self.ambulanceY-1][self.ambulanceX] = AMBULANCE_CH
                self.map[self.ambulanceY-2][self.ambulanceX] = str(int(self.map[self.ambulanceY-2][self.ambulanceX])-1)
                self.ambulanceY-=1
                return True
        elif self.ambulanceY > 2 and self.map[self.ambulanceY-1][self.ambulanceX] == PATIENT_CH and self.map[self.ambulanceY-2][self.ambulanceX] == SPACE_CH:
            self.map[self.ambulanceY][self.ambulanceX] = SPACE_CH
            self.ambulanceY-=1
            self.map[self.ambulanceY][self.ambulanceX] = AMBULANCE_CH
            self.map[self.ambulanceY-1][self.ambulanceX] = PATIENT_CH
            return True
        elif self.ambulanceY > 1 and self.map[self.ambulanceY-1][self.ambulanceX] == SPACE_CH:
            self.map[self.ambulanceY][self.ambulanceX] = SPACE_CH
            self.ambulanceY-=1
            self.map[self.ambulanceY][self.ambulanceX] = AMBULANCE_CH
            return True
        else:
            return False

    def moveDown(self):
        if self.ambulanceY < self.height - 3 and self.map[self.ambulanceY+1][self.ambulanceX] == PATIENT_CH and self.map[self.ambulanceY+2][self.ambulanceX].isnumeric():
            if int(self.map[self.ambulanceY+2][self.ambulanceX]) > 0:
                self.map[self.ambulanceY][self.ambulanceX] = SPACE_CH
                self.map[self.ambulanceY+1][self.ambulanceX] = AMBULANCE_CH
                self.map[self.ambulanceY+2][self.ambulanceX] = str(int(self.map[self.ambulanceY+2][self.ambulanceX])-1)
                self.ambulanceY+=1
                return True
        elif self.ambulanceY < len(self.map) - 3 and self.map[self.ambulanceY+1][self.ambulanceX] == PATIENT_CH and self.map[self.ambulanceY+2][self.ambulanceX] == SPACE_CH:
            self.map[self.ambulanceY][self.ambulanceX] = SPACE_CH
            self.ambulanceY+=1
            self.map[self.ambulanceY][self.ambulanceX] = AMBULANCE_CH
            self.map[self.ambulanceY+1][self.ambulanceX] = PATIENT_CH
            return True
        elif self.ambulanceY < len(self.map) - 2 and self.map[self.ambulanceY+1][self.ambulanceX] == SPACE_CH:
            self.map[self.ambulanceY][self.ambulanceX] = SPACE_CH
            self.ambulanceY+=1
            self.map[self.ambulanceY][self.ambulanceX] = AMBULANCE_CH
            return True
        else:
            return False

def DFS(originalMap, currentState, maxDepth, currentDepth, reached, moves, depths):
    currentState.isThisStateGoalState()
    originalMap.numOfallExploredStates+=1
    if currentState.isGoalState:
        return currentState
    if currentDepth >= maxDepth:
        return None
    if currentState.hashMap in reached:
        if depths[currentState.hashMap] <= currentDepth:
            return None
    else:
        originalMap.numOfUniqueExploredStates+=1
    
    depths[currentState.hashMap] = currentDepth
    reached.add(currentState.hashMap)
    originalMap.allReached.add(currentState.hashMap)

    for move in moves:
        originalMap.changeMap(currentState.hashMap)
        if move == 'up':
            originalMap.moveUp()
        elif move == 'down':
            originalMap.moveDown()
        elif move == 'left':
            originalMap.moveLeft()
        else:
            originalMap.moveRight()
        newState = state(originalMap.ambulanceX, originalMap.ambulanceY, originalMap.map, currentState)
        currentDepth = currentDepth + 1
        goal = DFS(originalMap, newState, maxDepth, currentDepth, reached, moves, depths)
        if goal is not None:
            return goal
    return None

def IDS(originalMap):
    moves = ['up', 'down', 'left', 'right']
    initialState = state(originalMap.ambulanceX, originalMap.ambulanceY, originalMap.map, None)
    originalMap.numOfallExploredStates+=1
    originalMap.numOfUniqueExploredStates+=1
    maxDepth = 0
    while True:
        maxDepth += 1
        reachedSet = set()
        depthDic = dict()
        tempState = DFS(originalMap, initialState, maxDepth, 0, reachedSet, moves, depthDic)
        if tempState is not None:
            return tempState

fileNames = ["test1.txt", "test2.txt", "test3.txt"]
cntr = 1
for fileName in fileNames:
    m = mapActions("../testcases/" + fileName)
    s = time()
    finalState = (IDS(m))
    e = time()
    print("test number " + str(cntr))
    print("Time: " + str(e - s) + "s")
    print("Depth of goal is " + str(finalState.level))
    print("Number of all explored states are: " + str(m.numOfallExploredStates))
    print("Number of unique explored states are: " + str(len(m.allReached)))
    cntr+=1

    