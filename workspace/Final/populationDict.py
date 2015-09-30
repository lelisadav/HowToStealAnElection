# -*- coding: utf-8 -*-
"""
Created on Sun Sep 27 18:39:58 2015

@author: ellie
"""
import requests
import json
class PopulationDictTract():
    def __init__(self):
        self.pDict=dict()
        
    def fillPopulation(self, state, county):
        url='http://api.census.gov/data/2010/sf1?get=P0010001&for=tract:*&in=state:'+state+'+county:'+county+'&key=3491625ba162b732cd9cf659d4d4d4aee437c7f5'
        response = requests.get(url)
        if(response.ok):
            jData = json.loads(response.content)
            i=0
            for key in jData:
                if (i>=1):
                    tract=key[3]
                    dKey=state+county+tract
#                    print(int(key[0]))
                    self.pDict[dKey]=int(key[0])
                i+=1
        else:
            response.raise_for_status()
    def getPopulation(self, state, county, tract):
        dKey=state+county+tract
        return self.pDict[dKey]
    def writeMaxMin(self):
        v=list(self.pDict.values())
        maxP=max(v)
        minP=min(v)
        self.pDict['max']=maxP
        self.pDict['min']=minP
    def getMax(self):
        return self.pDict['max']
    def getMin(self):
        return self.pDict['min']
    def writeToFile(self, fileName):
        with open(fileName, 'w') as fp:
            json.dump(self.pDict, fp)
    def readFromFile(self, fileName):
         with open(fileName, 'r') as fp:
            self.pDict=json.load(fp)
        
class PopulationDictBlock():
    def __init__(self):
        self.pDict=dict()
        
    def fillPopulation(self, state, county, tract):
        url='http://api.census.gov/data/2010/sf1?get=P0010001&for=block:*&in=state:'+state+'+county:'+county+'+tract:'+tract+'&key=3491625ba162b732cd9cf659d4d4d4aee437c7f5'
        response = requests.get(url)
        if(response.ok):
            jData = json.loads(response.content)
            i=0
            for key in jData:
                if (i>=1):
                    block=key[4]
                    dKey=state+county+tract+block
#                    print(int(key[0]))
                    self.pDict[dKey]=int(key[0])
                i+=1
        else:
            response.raise_for_status()
    def getPopulation(self, state, county, tract, block):
        dKey=state+county+tract+block
        return self.pDict[dKey]
    def writeMaxMin(self):
        v=list(self.pDict.values())
        maxP=max(v)
        minP=min(v)
        self.pDict['max']=maxP
        self.pDict['min']=minP
    def getMax(self):
        return self.pDict['max']
    def getMin(self):
        return self.pDict['min']
    def writeToFile(self, fileName):
        with open(fileName, 'w') as fp:
            json.dump(self.pDict, fp)
    def readFromFile(self, fileName):
         with open(fileName, 'r') as fp:
            self.pDict=json.load(fp)
class PopulationDictCounty():
    def __init__(self):
        self.pDict=dict()
        
    def fillPopulation(self, state):
        url='http://api.census.gov/data/2010/sf1?get=P0010001&for=county:*&in=state:'+state+'&key=3491625ba162b732cd9cf659d4d4d4aee437c7f5'
        response = requests.get(url)
        if(response.ok):
            jData = json.loads(response.content)
            i=0
            for key in jData:
                if (i>=1):
                    county=key[2]
                    dKey=state+county
#                    print(int(key[0]))
                    self.pDict[dKey]=int(key[0])
                i+=1
        else:
            response.raise_for_status()
    def getPopulation(self, state, county):
        dKey=state+county
        return self.pDict[dKey]
    def writeMaxMin(self):
        v=list(self.pDict.values())
        maxP=max(v)
        minP=min(v)
        self.pDict['max']=maxP
        self.pDict['min']=minP
    def getMax(self):
        return self.pDict['max']
    def getMin(self):
        return self.pDict['min']
    def writeToFile(self, fileName):
        with open(fileName, 'w') as fp:
            json.dump(self.pDict, fp)
    def readFromFile(self, fileName):
         with open(fileName, 'r') as fp:
            self.pDict=json.load(fp)
