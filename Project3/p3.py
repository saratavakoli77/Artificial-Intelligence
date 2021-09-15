import pandas as pd
import nltk
import re
import math
import sys
import random

FEILD = 'short_description'
FILELOCATION = "Attachment/data.csv"
TESTFILELOCATION = "Attachment/test.csv"
CATEGORYCOL = 'category'
BUSINESSCATEGORY = 'BUSINESS'
STYLEANDBEAUTYCATEGORY = 'STYLE & BEAUTY'
TRAVELCATEGORY = 'TRAVEL'

class Category:
    def __init__(self, categoyName):
        self.name = categoyName
        self.accuracyPhase1 = 0
        self.precisionPhase1 = 0
        self.recallPhase1 = 0
        self.accuracyPhase2 = 0
        self.precisionPhase2 = 0
        self.recallPhase2 = 0
        self.p = 0
        
    def calculateProbabilityOfWords(self, data):
        self.wordsProbability = {}
        wordsNum = {}
        lenOfDescription = data[FEILD].apply(lambda x: len(x))
        s = 0
        for num in lenOfDescription:
            s += num
        self.lenOfAllWords = s
        self.allWords = set()
        for arr in data[FEILD]:
            for word in arr:
                if word not in self.allWords:
                    wordsNum[word] = 2
                    self.allWords.add(word)
                else:
                    wordsNum[word] += 1

        for x in wordsNum:
            self.wordsProbability[x] = round(wordsNum[x]*100/self.lenOfAllWords, 8)

def readData(fileLoc):
    return pd.read_csv(fileLoc)

def removeRowsWithNanDescription(data, textField):
    data = data[data['short_description'].notnull()]
    return data

def changeUpperCaseCharsWithLower(data, textField):
    data[textField] = data[textField].str.lower()
    return data

def removeSymbolsAnsNums(data, textField):
    data[textField] = data[textField].apply(lambda elem: re.sub(r"(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)|^rt|http.+?", "", elem))  
    data[textField] = data[textField].apply(lambda elem: re.sub(r"\d+", "", elem))
    return data

def cleanText(data, textField):
    data = changeUpperCaseCharsWithLower(data, textField)
    data = removeSymbolsAnsNums(data, textField)
    return data

def removeStopWords(data, textField):
    from nltk.corpus import stopwords
    stop = nltk.corpus.stopwords.words('english')
    data[textField] = data[textField].apply(lambda x: ' '.join([word for word in x.split() if word not in (stop)]))
    return data

def tokenise(data, textField):
    nltk.download('punkt')
    data[textField] = data[textField].apply(lambda x: nltk.tokenize.word_tokenize(x))
    return data

def wordStemmer(text):
    stem_text = [nltk.stem.PorterStemmer().stem(i) for i in text]
    return stem_text

def stemmingText(data, textField):
    data[textField] = data[textField].apply(lambda x: wordStemmer(x))
    return data

def wordLemmatizer(text):
    lem_text = [nltk.stem.WordNetLemmatizer().lemmatize(i) for i in text]
    return lem_text

def lemmatizeText(data, textField):
    nltk.download('wordnet')
    data[textField] = data[textField].apply(lambda x: wordLemmatizer(x))
    return data

def normalizeData(fileLoc, textField):
    data = readData(fileLoc)
    data = removeRowsWithNanDescription(data, textField)
    data = changeUpperCaseCharsWithLower(data, textField)
    data = removeStopWords(data, textField)
    data = removeSymbolsAnsNums(data, textField)
    data = tokenise(data, textField)
    data = stemmingText(data, textField)
    # data = lemmatizeText(data, textField)
    return data

def prepareTrainigAndTestingData(fileLoc, fieldToNormalize):
    data = normalizeData(fileLoc, fieldToNormalize)
    businessCategory = data.loc[data[CATEGORYCOL] == BUSINESSCATEGORY]
    styleAndBeautyCategory = data.loc[data[CATEGORYCOL] == STYLEANDBEAUTYCATEGORY]
    travelCategory = data.loc[data[CATEGORYCOL] == TRAVELCATEGORY]
    trainingData = pd.concat([businessCategory.sample(frac = 0.8), styleAndBeautyCategory.sample(frac = 0.8), travelCategory.sample(frac = 0.8)])
    testingData = data.drop(trainingData.index)
    return trainingData, testingData

def calculateProbabilityOfEachWordInCategorys(field, oversampling1, oversampling2):
    categoriesPhase1 = []
    categoriesPhase2 = []
    if oversampling1 == False and oversampling2 == False:
        trainingData, testingData = prepareTrainigAndTestingData(FILELOCATION, FEILD)
    elif oversampling1:
        trainingData, testingData = dataForOversamplingPase1(FILELOCATION, FEILD)
    else:
        trainingData, testingData = dataForOversamplingPase2(FILELOCATION, FEILD)
    businessCategoryData = trainingData.loc[trainingData[CATEGORYCOL] == BUSINESSCATEGORY]
    businessCategory = Category(BUSINESSCATEGORY)
    businessCategory.calculateProbabilityOfWords(businessCategoryData)
    categoriesPhase2.append(businessCategory)
    categoriesPhase1.append(businessCategory)
    styleAndBeautyCategoryData = trainingData.loc[trainingData[CATEGORYCOL] == STYLEANDBEAUTYCATEGORY]
    styleAndBeautyCategory = Category(STYLEANDBEAUTYCATEGORY)
    styleAndBeautyCategory.calculateProbabilityOfWords(styleAndBeautyCategoryData)
    categoriesPhase2.append(styleAndBeautyCategory)
    travelCategoryData = trainingData.loc[trainingData[CATEGORYCOL] == TRAVELCATEGORY]
    travelCategory = Category(TRAVELCATEGORY)
    travelCategory.calculateProbabilityOfWords(travelCategoryData)
    categoriesPhase2.append(travelCategory)
    categoriesPhase1.append(travelCategory)
    return categoriesPhase1, categoriesPhase2, testingData

def predictCategory(words, categories):
    probabilities = {}
    s = 0
    for c in categories:
        s += c.lenOfAllWords
    for c in categories:
        c.p = round((c.lenOfAllWords * 100/s), 8)
    for category in categories:
        probabilityForWordsNotExistInCategory = round(100/category.lenOfAllWords, 8)
        probabilities[category.name] = math.log10(category.p)
        for word in words:
            if word in category.allWords:
                probabilities[category.name] += math.log10(category.wordsProbability[word])
            else:
                probabilities[category.name] += math.log10(probabilityForWordsNotExistInCategory)
    chosenCategory = ''
    maximum = -sys.maxsize - 1
    for p in probabilities:
        if probabilities[p] > maximum:
            maximum = probabilities[p]
            chosenCategory = p
    return chosenCategory

def predictForAllNewsPhase1():
    categoriesPhase1, categoriesPhase2, testingData = calculateProbabilityOfEachWordInCategorys(FEILD, False, False)
    testingData = testingData[~(testingData[CATEGORYCOL] == STYLEANDBEAUTYCATEGORY)]
    testingData['GUESS'] = testingData[FEILD].apply(lambda x: predictCategory(x, categoriesPhase1))
    return categoriesPhase1, categoriesPhase2, testingData

def evaluationPhase1():
    categoriesPhase1, categoriesPhase2, predictedData = predictForAllNewsPhase1()
    for category in categoriesPhase1:
        tp = len(predictedData[(predictedData[CATEGORYCOL] == category.name) & (predictedData["GUESS"] == category.name)])
        tn = len(predictedData[(predictedData[CATEGORYCOL] != category.name) & (predictedData["GUESS"] != category.name)])
        fp = len(predictedData[(predictedData[CATEGORYCOL] != category.name) & (predictedData["GUESS"] == category.name)])
        fn = len(predictedData[(predictedData[CATEGORYCOL] == category.name) & (predictedData["GUESS"] != category.name)])
        category.accuracyPhase1 = (tp + tn) / (tp + tn + fp + fn)
        category.precisionPhase1 = tp / (tp + fp)
        category.recallPhase1 = tp / (tp + fn)
    return categoriesPhase1

def predictForAllNewsPhase2():
    categoriesPhase1, categoriesPhase2, testingData = calculateProbabilityOfEachWordInCategorys(FEILD, False, False)
    testingData['GUESS'] = testingData[FEILD].apply(lambda x: predictCategory(x, categoriesPhase2))
    return categoriesPhase2, testingData

def evaluationPhase2():
    categoriesPhase2, predictedData = predictForAllNewsPhase2()
    tpS = 0
    tnS = 0
    fpS = 0
    fnS = 0
    for category in categoriesPhase2:
        tp = len(predictedData[(predictedData[CATEGORYCOL] == category.name) & (predictedData["GUESS"] == category.name)])
        tn = len(predictedData[(predictedData[CATEGORYCOL] != category.name) & (predictedData["GUESS"] != category.name)])
        fp = len(predictedData[(predictedData[CATEGORYCOL] != category.name) & (predictedData["GUESS"] == category.name)])
        fn = len(predictedData[(predictedData[CATEGORYCOL] == category.name) & (predictedData["GUESS"] != category.name)])
        category.accuracyPhase2 = (tp + tn) / (tp + tn + fp + fn)
        category.precisionPhase2 = tp / (tp + fp)
        category.recallPhase2 = tp / (tp + fn)
        tpS += tp
        tnS += tn
        fpS += fp
        fnS += fn
    #     print(category.name)
    #     print("tp", tp, "tn", tn, "fp", fp, "fn", fn)
    # print("overal confusion matrix for phase 2:")
    # print("tp", tpS, "tn", tnS, "fp", fpS, "fn", fnS)
    return categoriesPhase2

categoryPhase1 = evaluationPhase1()
for c in categoryPhase1:
    print(c.name)
    print("accuracy ", c.accuracyPhase1)
    print("precision ", c.precisionPhase1)
    print("recall ", c.recallPhase1)

categoryFinalPhase2 = evaluationPhase2()
for c in categoryFinalPhase2:
    print(c.name)
    print("accuracy ", c.accuracyPhase2)
    print("precision ", c.precisionPhase2)
    print("recall ", c.recallPhase2)

def dataForOversamplingPase1(fileLoc, fieldToNormalize):
    data = normalizeData(fileLoc, fieldToNormalize)
    businessCategory = data.loc[data[CATEGORYCOL] == BUSINESSCATEGORY]
    travelCategory = data.loc[data[CATEGORYCOL] == TRAVELCATEGORY]
    businessCategory = businessCategory.sample(frac = 0.8)
    travelCategory = travelCategory.sample(frac = 0.8)
    difference = abs(len(businessCategory) - len(travelCategory))
    business = False
    travel = False
    if len(businessCategory) < len(travelCategory):
        lowerOne = businessCategory
        business = True
    else:
        lowerOne = travelCategory
        travel = True
    indexes = lowerOne.index
    temp = lowerOne
    while difference > 0:
        rand = random.choice(indexes)
        row = temp.loc[[rand]]
        lowerOne = pd.concat([lowerOne, row])
        difference-=1
    if business:
        businessCategory = lowerOne
    elif travel:
        travelCategory = lowerOne
    trainingData = pd.concat([businessCategory, travelCategory])    
    testingData = data.drop(trainingData.index)
    testingData = testingData[~(testingData[CATEGORYCOL] == STYLEANDBEAUTYCATEGORY)]
    return trainingData, testingData

def oversamplingPase1():
    categoriesPhase1, categoriesPhase2, testingData = calculateProbabilityOfEachWordInCategorys(FEILD, True, False)
    testingData['GUESS'] = testingData[FEILD].apply(lambda x: predictCategory(x, categoriesPhase1))
    for category in categoriesPhase1:
        tp = len(testingData[(testingData[CATEGORYCOL] == category.name) & (testingData["GUESS"] == category.name)])
        tn = len(testingData[(testingData[CATEGORYCOL] != category.name) & (testingData["GUESS"] != category.name)])
        fp = len(testingData[(testingData[CATEGORYCOL] != category.name) & (testingData["GUESS"] == category.name)])
        fn = len(testingData[(testingData[CATEGORYCOL] == category.name) & (testingData["GUESS"] != category.name)])
        category.accuracyPhase1 = (tp + tn) / (tp + tn + fp + fn)
        category.precisionPhase1 = tp / (tp + fp)
        category.recallPhase1 = tp / (tp + fn)
    return categoriesPhase1

categoryPhase1 = oversamplingPase1()
print("oversampling phase 1")
for c in categoryPhase1:
    print(c.name)
    print("accuracy ", c.accuracyPhase1)
    print("precision ", c.precisionPhase1)
    print("recall ", c.recallPhase1)

def dataForOversamplingPase2(fileLoc, fieldToNormalize):
    data = normalizeData(fileLoc, fieldToNormalize)
    businessCategory = data.loc[data[CATEGORYCOL] == BUSINESSCATEGORY]
    travelCategory = data.loc[data[CATEGORYCOL] == TRAVELCATEGORY]
    styleAndBeautyCategory = data.loc[data[CATEGORYCOL] == STYLEANDBEAUTYCATEGORY]
    businessCategory = businessCategory.sample(frac = 0.8)
    travelCategory = travelCategory.sample(frac = 0.8)
    styleAndBeautyCategory = styleAndBeautyCategory.sample(frac = 0.8)
    business = True
    travel = True
    style = True
    lenArr = [len(businessCategory), len(travelCategory), len(styleAndBeautyCategory)]
    maxLen = max(lenArr)
    smallerCategories = []
    if len(businessCategory) != maxLen:
        business = False
        smallerCategories.append(businessCategory)
    if len(travelCategory) != maxLen:
        travel = False
        smallerCategories.append(travelCategory)
    if len(styleAndBeautyCategory) != maxLen:
        style = False
        smallerCategories.append(styleAndBeautyCategory)
    if business:
        trainingData = businessCategory
    if travel:
        trainingData = travelCategory
    if style:
        trainingData = styleAndBeautyCategory
    for category in smallerCategories:
        indexes = category.index
        temp = category
        while len(category) < maxLen:
            rand = random.choice(indexes)
            row = temp.loc[[rand]]
            category = pd.concat([category, row])
        trainingData = pd.concat([trainingData, category])
    
    testingData = data.drop(trainingData.index)
    return trainingData, testingData

def oversamplingPase2():
    categoriesPhase1, categoriesPhase2, testingData = calculateProbabilityOfEachWordInCategorys(FEILD, False, True)
    testingData['GUESS'] = testingData[FEILD].apply(lambda x: predictCategory(x, categoriesPhase2))
    for category in categoriesPhase2:
        print(category.name)
        tp = len(testingData[(testingData[CATEGORYCOL] == category.name) & (testingData["GUESS"] == category.name)])
        tn = len(testingData[(testingData[CATEGORYCOL] != category.name) & (testingData["GUESS"] != category.name)])
        fp = len(testingData[(testingData[CATEGORYCOL] != category.name) & (testingData["GUESS"] == category.name)])
        fn = len(testingData[(testingData[CATEGORYCOL] == category.name) & (testingData["GUESS"] != category.name)])
        category.accuracyPhase2 = (tp + tn) / (tp + tn + fp + fn)
        category.precisionPhase2 = tp / (tp + fp)
        category.recallPhase2 = tp / (tp + fn)
    return categoriesPhase2

categoryPhase2 = oversamplingPase2()
print("oversampling phase 2")
for c in categoryPhase2:
    print(c.name)
    print("accuracy ", c.accuracyPhase2)
    print("precision ", c.precisionPhase2)
    print("recall ", c.recallPhase2)


def test(categoryFinalPhase2):
    data = normalizeData(TESTFILELOCATION, FEILD)
    data['category'] = data[FEILD].apply(lambda x: predictCategory(x, categoryFinalPhase2))
    data = data[['index', 'category']]
    data.drop(data.columns[1], axis=1)
    data.to_csv('out.csv')

test(categoryFinalPhase2)
