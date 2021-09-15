import re
import random
from time import time

POPULATIONNUMBER = 800
CROSSOVERPOINTSNUMBER = 6
MUTATIONPROBABILITY = 0.1
CROSSOVERPROBABILITY = 0.7
SWAPPAIRSNUMBER = 1

class Key:
    def __init__(self):
        self.key = {}
        self.hashKey = ''
        self.fitness = 0
        self.isTheAnswer = False
        self.unMeaningfulWords = []

class Decoder:
    def __init__(self, encodedText):
        self.encodedText = encodedText
        allWords = open("global_text.txt", "r")
        dictionary = set(re.findall("[a-zA-Z]+", allWords.read()))
        self.encodedWords = set(re.findall("[a-zA-Z]+", self.encodedText))
        self.dictionary = dictionary
        self.population = []
        self.hashKey = []
        self.matingPool = []
        self.answerFounded = False
        self.bestOfThisGeneration = None
        self.decodedText = ''
        self.answer = None

    def addKeyToPopulation(self):
        tempKey = Key()
        rand = random.sample(range(97, 123), 26)
        hashOfKey = ""
        for i in range(len(rand)):
            tempKey.key[chr(i+97)] = chr(rand[i])
            hashOfKey += chr(i+97) + " : " + tempKey.key[chr(i+97)] + "\n"
        if hashOfKey not in self.hashKey:
            self.hashKey.append(hashOfKey)
            tempKey.hashKey = hashOfKey
        self.population.append(tempKey)

    def createPopulation(self):
        cnt = 0
        while len(self.population) != POPULATIONNUMBER:
            self.addKeyToPopulation()
            self.calculateFitness(self.population[cnt])
            cnt+=1

    def calculateFitness(self, key):
        compiledWords = []
        for word in self.encodedWords:
            tempList = list(word)
            for i in range(len(word)):
                if ord(word[i]) < 97:
                    char = chr(ord(word[i])+32)
                    smallLetter = key.key[char]
                    tempList[i] = chr(ord(smallLetter)-32)
                else:
                    tempList[i] = key.key[word[i]]
            tempStr = "".join(tempList)
            compiledWords.append(tempStr)
        lenSum = 0
        numberOfUnmeaningfull = 0
        for word in compiledWords:
            if word in self.dictionary:
                lenSum += len(word)
            else:
                key.unMeaningfulWords.append(word)
                numberOfUnmeaningfull+=1
        key.fitness = lenSum
        if numberOfUnmeaningfull == 0:
            key.isTheAnswer = True
            self.answerFounded = True
            self.answer = key
    
    def calculateFitnessForPopulation(self):
        maxFitnessInGeneration = 0
        a = Key()
        answer = None
        for individual in self.population:
            self.calculateFitness(individual)
            if individual.fitness > maxFitnessInGeneration:
                maxFitnessInGeneration = individual.fitness
                self.bestOfThisGeneration = individual
                a = individual
            if individual.isTheAnswer == True:
                self.answerFounded = True
                answer = individual
                self.answer = answer
                return answer
        return answer

    def createMatingPool(self):
        sortedByFitness = []
        sortedByFitness = sorted(self.population, key = lambda x : x.fitness, reverse = False)
        rankSum = (len(sortedByFitness)*(len(sortedByFitness)+1))/2
        checkSum = 0
        ranks = []
        for i in range(len(sortedByFitness)):
            sortedByFitness[i].rankP = round(((i+1)/rankSum)*100,3)
            ranks.append(sortedByFitness[i].rankP)
        self.matingPool = random.choices(sortedByFitness, weights = ranks, k = POPULATIONNUMBER)

    def substitutionDuplicateCharInChilds(self, childKey1,childKey2):
        alphabet = childKey1.keys()
        key1Used = set(list(childKey1.values()))
        key2Used = set(list(childKey2.values()))
        child1values = list(childKey1.values())
        child2values = list(childKey2.values())
        key1UnUsed = []
        key2UnUsed = []
        for char in alphabet:
            if char not in key1Used:
                key1UnUsed.append(char)
            if char not in key2Used:
                key2UnUsed.append(char)
        randNum1 = random.sample(range(0, len(key1UnUsed)), len(key1UnUsed))
        randNum2 = random.sample(range(0, len(key2UnUsed)), len(key2UnUsed))
        for i in range(26):
            for j in range(i+1, 26):
                if child1values[i] == child1values[j]:
                    child1values[j] = key1UnUsed[randNum1.pop(0)]
                if child2values[i] == child2values[j]:
                    child2values[j] = key2UnUsed[randNum2.pop(0)]
        childKey1 = (dict(zip(alphabet, child1values)))
        childKey2 = (dict(zip(alphabet, child2values)))
        return childKey1, childKey2

    def crossover(self, parent1, parent2):
        crossoverPoints = random.sample(range(1, 25), CROSSOVERPOINTSNUMBER)
        crossoverPoints.append(26)
        crossoverPoints.sort()
        tempKey = parent1.key
        tempKey2 = parent2.key
        parent1Values = list(tempKey.values())
        parent2Values = list(tempKey2.values())
        childKey1 = {}
        childKey2 = {}
        for i in range(26):
            childKey1[chr(i+97)] = ''
            childKey2[chr(i+97)] = ''
        prevPoint = 0
        pointIndex = 0
        for point in crossoverPoints:
            partOfParent1 = parent1Values[prevPoint:point]
            partOfParent2 = parent2Values[prevPoint:point]
            for i in range(prevPoint, point):
                if (pointIndex % 2) == 0:
                    childKey1[chr(i+97)] = partOfParent1[i-prevPoint]
                    childKey2[chr(i+97)] = partOfParent2[i-prevPoint]
                else:
                    childKey1[chr(i+97)] = partOfParent2[i-prevPoint]
                    childKey2[chr(i+97)] = partOfParent1[i-prevPoint]
            prevPoint = point
            pointIndex+=1
        childKey1, childKey2 = self.substitutionDuplicateCharInChilds(childKey1, childKey2)
        child1 = Key()
        child2 = Key()
        child1.key = childKey1
        child2.key = childKey2
        return child1, child2

    def mutation(self, child, numOfKeys):
        for i in range(numOfKeys):
            rand1 = random.randrange(97, 123)
            rand2 = random.randrange(97, 123)
            tempValue = child.key[chr(rand1)]
            child.key[chr(rand1)] = child.key[chr(rand2)]
            child.key[chr(rand1)] = tempValue
        return child

    def crossoverAndMutation(self, parent1, parent2, numOfKeys):
        child1, child2 = self.crossover(parent1, parent2)
        child1 = self.mutation(child1, numOfKeys)
        child2 = self.mutation(child2, numOfKeys)
        return child1, child2
    
    def createNextGeneration(self):
        random.shuffle(self.matingPool)
        newGeneration = []
        for i in range(0, len(self.matingPool), 2):
            crossoverProbability = random.uniform(0,1)
            mutationProbability = random.uniform(0,1)
            if crossoverProbability <= CROSSOVERPROBABILITY:
                child1 = Key()
                child2 = Key()
                if mutationProbability <= MUTATIONPROBABILITY:
                    child1, child2 = self.crossoverAndMutation(self.matingPool[i], self.matingPool[i+1], SWAPPAIRSNUMBER)
                else:
                    child1, child2 = self.crossover(self.matingPool[i], self.matingPool[i+1])
                newGeneration.append(child1)
                newGeneration.append(child2)
            else:
                newGeneration.append(self.matingPool[i])
                newGeneration.append(self.matingPool[i+1])
        return newGeneration
    
    def GA(self):
        self.createPopulation()
        n = 2000
        numOfGenerations = 0
        while self.answerFounded == False and n > 0:
            numOfGenerations+=1
            self.createMatingPool()
            self.population = self.createNextGeneration()
            answer = self.calculateFitnessForPopulation()
            # print(numOfGenerations)
            # if answer:
            #     print(answer.key)
            # else:
            #     print(answer)
            # print(self.bestOfThisGeneration.key)
            # print("----------------------------------------------------")
            n-=1
        # print(self.answer.key)

    def decode(self):
        self.GA()
        decodedText = ''
        for char in self.encodedText:
            if ord(char) >= 97 and ord(char) <= 122:
                decodedText += self.answer.key[char]
            elif ord(char) >= 65 and ord(char) <= 90:
                temp = chr(ord(char)+32)
                smallLetter = self.answer.key[temp]
                decodedText += smallLetter.capitalize()
            else:
                decodedText += char
        self.decodedText = decodedText
        return self.decodedText

start = time()
encoded_text = open("encoded_text.txt", "r").read()
d = Decoder(encoded_text)
decoded_text = d.decode()
print(decoded_text)
end = time()
print("Time: " + str(end - start) + "s")