import heapq
from time import time

OBSTACLE_CH = '#'
AMBULANCE_CH = 'A'
PATIENT_CH = 'P'
SPACE_CH = ' '
 
class PriorityQueue:
    def __init__(self):
        self._queue = []
        self._index = 0
        self.size = 0
 
    def push(self, item, priority):
        heapq.heappush(self._queue, (priority, self._index, item))
        self._index += 1
        self.size += 1
 
    def pop(self):
        self.size -= 1
        return heapq.heappop(self._queue)[-1]

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

class state:
    def __init__(self, ambulanceX, ambulanceY, newMap, parent):
        self.ambulanceX = ambulanceX
        self.ambulanceY = ambulanceY
        self.createHash(newMap)
        self.parent = parent
        self.setLevel()
        self.map = newMap
        self.patientsPlace = []
        self.hospitalsPlace = []
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
    def calculateH(self):
        currentCost = self.level
        distanceFromAmbulanceToPatients = 0
        mapX = len(self.map[0])
        mapY = len(self.map)
        minDistanceFromPatients = float("inf")
        for i in range(mapY):
            for j in range(mapX):
                if self.map[i][j] == PATIENT_CH:
                    tempDis = abs(i-self.ambulanceY) + abs(j-self.ambulanceX)
                    if tempDis < minDistanceFromPatients:
                        minDistanceFromPatients = tempDis
                    self.patientsPlace.append(j)
                    self.patientsPlace.append(i)
                elif self.map[i][j].isnumeric() and self.map[i][j] != '0':
                    self.hospitalsPlace.append(j)
                    self.hospitalsPlace.append(i)
        distanceFromPatientsToHospitals = 0
        for i in range(0, len(self.patientsPlace), 2):
            minDistanceFromHospitals = float("inf")
            for j in range(0, len(self.hospitalsPlace), 2):
                tempDistance = abs(self.hospitalsPlace[j]-self.patientsPlace[i])+abs(self.hospitalsPlace[j+1]-self.patientsPlace[i+1])
                if tempDistance < minDistanceFromHospitals:
                    tempDistance = minDistanceFromHospitals
            distanceFromPatientsToHospitals += tempDistance
        return minDistanceFromPatients + distanceFromPatientsToHospitals + currentCost

def BFS(originalMap):
    moves = ['up', 'down', 'left', 'right']
    frontier = PriorityQueue()
    visited = set()
    reached = set()
    initialState = state(originalMap.ambulanceX, originalMap.ambulanceY, originalMap.map, None)
    frontier.push(initialState, initialState.calculateH())
    visited.add(initialState.hashMap)
    originalMap.numOfallExploredStates+=1
    originalMap.numOfUniqueExploredStates+=1
    while frontier.size:
        nowState = frontier.pop()
        reached.add(nowState.hashMap)
        for move in moves:
            originalMap.changeMap(nowState.hashMap)
            if move == 'up':
                originalMap.moveUp()
            elif move == 'down':
                originalMap.moveDown()
            elif move == 'left':
                originalMap.moveLeft()
            else:
                originalMap.moveRight()
            newState = state(originalMap.ambulanceX, originalMap.ambulanceY, originalMap.map, nowState)
            originalMap.numOfallExploredStates+=1
            if newState.hashMap not in visited:
                originalMap.numOfUniqueExploredStates+=1
                thereIsPatient = False
                for line in newState.map:
                    if PATIENT_CH in line:
                        thereIsPatient = True
                        break
                if not thereIsPatient:
                    return newState
                else:
                    frontier.push(newState, newState.calculateH())
                    visited.add(newState.hashMap)
    return None

fileNames = ["test1.txt", "test2.txt", "test3.txt"]
cntr = 1
for fileName in fileNames:
    m = mapActions("../testcases/" + fileName)
    s = time()
    finalState = (BFS(m))
    e = time()
    print("test number " + str(cntr))
    print("Time: " + str(e - s) + "s")
    print("Depth of goal is " + str(finalState.level))
    print("Number of all explored states are: " + str(m.numOfallExploredStates))
    print("Number of unique explored states are: " + str(m.numOfUniqueExploredStates))
    cntr+=1
