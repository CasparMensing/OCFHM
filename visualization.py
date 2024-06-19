# -*- coding: utf-8 -*-
"""
Created on Tue Apr 16 11:10:12 2024

@author: Caspar Mensing
"""

from ocpa.objects.log.importer.ocel import factory as ocel_import_factory
import pandas as pd
import pm4py
import networkx as nx
import numpy as np
import pickle
import copy
from random import randrange
import json
#%%
filepath = ''#'output/'

with open(filepath + 'p2p-normal__unconsumable_inputBindings.pkl', 'rb') as f:
    inputBindings = pickle.load(f)

with open(filepath + 'p2p-normal__unconsumable_outputBindings.pkl', 'rb') as f:
    outputBindings = pickle.load(f)

with open(filepath + 'p2p-normal__unconsumable_activityCount.pkl', 'rb') as f:
    activityCount = pickle.load(f)

#dependencyGraph = nx.read_gexf(filepath + 'ContainerLogistics_Customer Order_Transport Document_Container_Handling Unit_unconsumable_dependencyGraph.xml')
with open(filepath + 'p2p-normal__unconsumable_dependencyGraph.pkl', 'rb') as f:
    dependencyGraph = pickle.load(f)
#%%

def filter0(inputBindings, outputBindings, threshold):
    filteredOutputBindings = {act : [] for act in outputBindings.keys()}
    for act in filteredOutputBindings.keys():
        for binding in outputBindings[act]:
            if binding[1]/activityCount[act] > threshold or any(binding[1]/activityCount[act2[0]] > threshold for act2 in binding[0]):
                filteredOutputBindings[act].append(binding)
    filteredInputBindings = {act : [] for act in inputBindings.keys()}
    for act in filteredInputBindings.keys():
        for binding in inputBindings[act]:
            if binding[1]/activityCount[act] > threshold or any(binding[1]/activityCount[act2[0]] > threshold for act2 in binding[0]):
                filteredInputBindings[act].append(binding)
    return filteredInputBindings, filteredOutputBindings

def filter1(inputBindings, outputBindings, threshold):
    filteredOutputBindings = {act : [] for act in outputBindings.keys()}
    for act in outputBindings.keys():
        for binding in outputBindings[act]:
            if binding[1]/activityCount[act] > threshold and all(any(count[1]/activityCount[act2[0]] > threshold for count in [binding2 for binding2 in inputBindings[act2[0]] if (act, act2[1]) in [(i[0], i[1]) for i in binding2[0]]]) for act2 in binding[0]):
                filteredOutputBindings[act].append(binding)
    filteredInputBindings = {act : [] for act in inputBindings.keys()}
    for act in inputBindings.keys():
        for binding in inputBindings[act]:
            if binding[1]/activityCount[act] > threshold and all(any(count[1]/activityCount[act2[0]] > threshold for count in [binding2 for binding2 in outputBindings[act2[0]] if (act, act2[1]) in [(i[0], i[1]) for i in binding2[0]]]) for act2 in binding[0]):
                filteredInputBindings[act].append(binding)
    return filteredInputBindings, filteredOutputBindings

def filter2(inputBindings, outputBindings, threshold):
    filteredOutputBindings = {act : [] for act in outputBindings.keys()}
    for act in filteredOutputBindings.keys():
        for binding in outputBindings[act]:
            if binding[1]/activityCount[act] > threshold and all(binding[1]/activityCount[act2[0]] > threshold for act2 in binding[0]):
                filteredOutputBindings[act].append(binding)
    filteredInputBindings = {act : [] for act in inputBindings.keys()}
    for act in filteredInputBindings.keys():
        for binding in inputBindings[act]:
            if binding[1]/activityCount[act] > threshold and all(binding[1]/activityCount[act2[0]] > threshold for act2 in binding[0]):
                filteredInputBindings[act].append(binding)
    return filteredInputBindings, filteredOutputBindings

def filter3(inputBindings, outputBindings, threshold):
    
    def getMostFrequent(bindings):
        mostFrequentBinding = bindings[[x[1] for x in bindings].index(max([x[1] for x in bindings]))]
        return mostFrequentBinding
    
    def getSubsequentInputBidnings(mostFrequentBinding, activity):
        for obligation in mostFrequentBinding[0]:
            if obligation[0] in inputBindings.keys():
                possibleInputBindings = [x for x in inputBindings[obligation[0]] if (activity, obligation[1]) in [(y[0], y[1]) for y in x[0]]]
                mostFrequentBinding = getMostFrequent(possibleInputBindings)
                addToFilteredInputBindings(mostFrequentBinding, obligation[0])
                
    def addToFilteredOutputBindings(mostFrequentBinding, activity):
        if mostFrequentBinding not in filteredOutputBindings[activity]:
            filteredOutputBindings[activity].append(mostFrequentBinding)
            getSubsequentInputBidnings(mostFrequentBinding, activity)
            
    def getSubsequentOutputBidnings(mostFrequentBinding, activity):
        for obligation in mostFrequentBinding[0]:
            if obligation[0] in outputBindings.keys():
                possibleOutputBindings = [x for x in outputBindings[obligation[0]] if (activity, obligation[1]) in [(y[0], y[1]) for y in x[0]]]
                mostFrequentBinding = getMostFrequent(possibleOutputBindings)
                addToFilteredOutputBindings(mostFrequentBinding, obligation[0])
                
    def addToFilteredInputBindings(mostFrequentBinding, activity):
        if mostFrequentBinding not in filteredInputBindings[activity]:
            filteredInputBindings[activity].append(mostFrequentBinding)
            getSubsequentOutputBidnings(mostFrequentBinding, activity)
    
    filteredOutputBindings = {act : [] for act in outputBindings.keys()}
    filteredInputBindings = {act : [] for act in inputBindings.keys()}
    
    for act in filteredOutputBindings.keys():
        mostFrequentBinding = getMostFrequent(outputBindings[act])
        addToFilteredOutputBindings(mostFrequentBinding, act)
    
    for act in filteredInputBindings.keys():
        mostFrequentBinding = getMostFrequent(inputBindings[act])
        addToFilteredInputBindings(mostFrequentBinding, act)
            
    return filteredInputBindings, filteredOutputBindings

def filter3_5(inputBindings, outputBindings, threshold):
    
    def getMostFrequent(bindings):
        mostFrequentBinding = bindings[[x[1] for x in bindings].index(max([x[1] for x in bindings]))]
        return mostFrequentBinding
    
    def getSubsequentInputBidnings(mostFrequentBinding, activity):
        for obligation in mostFrequentBinding[0]:
            if obligation[0] in inputBindings.keys():
                possibleInputBindings = [x for x in inputBindings[obligation[0]] if (activity, obligation[1]) in [(y[0], y[1]) for y in x[0]]]
                mostFrequentBinding = getMostFrequent(possibleInputBindings)
                addToFilteredInputBindings(mostFrequentBinding, obligation[0])
                
    def addToFilteredOutputBindings(mostFrequentBinding, activity):
        if mostFrequentBinding not in filteredOutputBindings[activity]:
            filteredOutputBindings[activity].append(mostFrequentBinding)
            getSubsequentInputBidnings(mostFrequentBinding, activity)
            
    def getSubsequentOutputBidnings(mostFrequentBinding, activity):
        for obligation in mostFrequentBinding[0]:
            if obligation[0] in outputBindings.keys():
                possibleOutputBindings = [x for x in outputBindings[obligation[0]] if (activity, obligation[1]) in [(y[0], y[1]) for y in x[0]]]
                mostFrequentBinding = getMostFrequent(possibleOutputBindings)
                addToFilteredOutputBindings(mostFrequentBinding, obligation[0])
                
    def addToFilteredInputBindings(mostFrequentBinding, activity):
        if mostFrequentBinding not in filteredInputBindings[activity]:
            filteredInputBindings[activity].append(mostFrequentBinding)
            getSubsequentOutputBidnings(mostFrequentBinding, activity)
    
    filteredOutputBindings = {act : [] for act in outputBindings.keys()}
    filteredInputBindings = {act : [] for act in inputBindings.keys()}
    
    for act in filteredOutputBindings.keys():
        if act[0:6] == 'START_':
            mostFrequentBindings = outputBindings[act]
            for binding in mostFrequentBindings:
                addToFilteredOutputBindings(binding, act)
        else:
            mostFrequentBinding = getMostFrequent(outputBindings[act])
            addToFilteredOutputBindings(mostFrequentBinding, act)
    
    for act in filteredInputBindings.keys():
        if act[-4:] == '_END':
            mostFrequentBindings = inputBindings[act]
            for binding in mostFrequentBindings:
                addToFilteredInputBindings(binding, act)
        else:
            mostFrequentBinding = getMostFrequent(inputBindings[act])
            addToFilteredInputBindings(mostFrequentBinding, act)
            
    return filteredInputBindings, filteredOutputBindings


def filter4(inputBindings, outputBindings, threshold):
    
    def filterByTreshold(bindings, activity):
        filteredBindings = [x for x in bindings if x[1]/activityCount[activity] > threshold]
        return filteredBindings
    
    def getMostFrequent(bindings):
        mostFrequentBinding = bindings[[x[1] for x in bindings].index(max([x[1] for x in bindings]))]
        return mostFrequentBinding
    
    def getSubsequentInputBidnings(mostFrequentBinding, activity):
        for obligation in mostFrequentBinding[0]:
            if obligation[0] in inputBindings.keys():
                possibleInputBindings = [x for x in inputBindings[obligation[0]] if (activity, obligation[1]) in [(y[0], y[1]) for y in x[0]]]
                mostFrequentBinding = getMostFrequent(possibleInputBindings)
                addToFilteredInputBindings(mostFrequentBinding, obligation[0])
                
    def addToFilteredOutputBindings(mostFrequentBinding, activity):
        if mostFrequentBinding not in filteredOutputBindings[activity]:
            filteredOutputBindings[activity].append(mostFrequentBinding)
            getSubsequentInputBidnings(mostFrequentBinding, activity)
            
    def getSubsequentOutputBidnings(mostFrequentBinding, activity):
        for obligation in mostFrequentBinding[0]:
            if obligation[0] in outputBindings.keys():
                possibleOutputBindings = [x for x in outputBindings[obligation[0]] if (activity, obligation[1]) in [(y[0], y[1]) for y in x[0]]]
                mostFrequentBinding = getMostFrequent(possibleOutputBindings)
                addToFilteredOutputBindings(mostFrequentBinding, obligation[0])
                
    def addToFilteredInputBindings(mostFrequentBinding, activity):
        if mostFrequentBinding not in filteredInputBindings[activity]:
            filteredInputBindings[activity].append(mostFrequentBinding)
            getSubsequentOutputBidnings(mostFrequentBinding, activity)
    
    filteredOutputBindings = {act : [] for act in outputBindings.keys()}
    filteredInputBindings = {act : [] for act in inputBindings.keys()}
    
    for act in filteredOutputBindings.keys():
        filteredBindings = filterByTreshold(outputBindings[act], act)
        for binding in filteredBindings:
            addToFilteredOutputBindings(binding, act)
    
    for act in filteredInputBindings.keys():
        filteredBindings = filterByTreshold(inputBindings[act], act)
        for binding in filteredBindings:
            addToFilteredInputBindings(binding, act)
            
    return filteredInputBindings, filteredOutputBindings


def filter5(inputBindings, outputBindings, threshold):
    
    def filterByTreshold(bindings, activity):
        filteredBindings = [x for x in bindings if x[1]/activityCount[activity] > threshold]
        for objectType in [x[0][1] for x in bindings]:
            if all([y[0][0] for y in filteredBindings if y[0][1] == objectType] == activity):
                filteredBindings.append(bindings[[x[0][1] for x in bindings].index(max([z[0][1] for z in bindings if z]))])
        return filteredBindings
    
    def getMostFrequent(bindings):
        mostFrequentBinding = bindings[[x[1] for x in bindings].index(max([x[1] for x in bindings]))]
        return mostFrequentBinding
    
    def getSubsequentInputBidnings(mostFrequentBinding, activity):
        for obligation in mostFrequentBinding[0]:
            if obligation[0] in inputBindings.keys():
                possibleInputBindings = [x for x in inputBindings[obligation[0]] if (activity, obligation[1]) in [(y[0], y[1]) for y in x[0]]]
                mostFrequentBinding = getMostFrequent(possibleInputBindings)
                addToFilteredInputBindings(mostFrequentBinding, obligation[0])
                
    def addToFilteredOutputBindings(mostFrequentBinding, activity):
        if mostFrequentBinding not in filteredOutputBindings[activity]:
            filteredOutputBindings[activity].append(mostFrequentBinding)
            getSubsequentInputBidnings(mostFrequentBinding, activity)
            
    def getSubsequentOutputBidnings(mostFrequentBinding, activity):
        for obligation in mostFrequentBinding[0]:
            if obligation[0] in outputBindings.keys():
                possibleOutputBindings = [x for x in outputBindings[obligation[0]] if (activity, obligation[1]) in [(y[0], y[1]) for y in x[0]]]
                mostFrequentBinding = getMostFrequent(possibleOutputBindings)
                addToFilteredOutputBindings(mostFrequentBinding, obligation[0])
                
    def addToFilteredInputBindings(mostFrequentBinding, activity):
        if mostFrequentBinding not in filteredInputBindings[activity]:
            filteredInputBindings[activity].append(mostFrequentBinding)
            getSubsequentOutputBidnings(mostFrequentBinding, activity)
    
    filteredOutputBindings = {act : [] for act in outputBindings.keys()}
    filteredInputBindings = {act : [] for act in inputBindings.keys()}
    
    for act in filteredOutputBindings.keys():
        filteredBindings = filterByTreshold(outputBindings[act], act)
        for binding in filteredBindings:
            addToFilteredOutputBindings(binding, act)
    
    for act in filteredInputBindings.keys():
        filteredBindings = filterByTreshold(inputBindings[act], act)
        for binding in filteredBindings:
            addToFilteredInputBindings(binding, act)
            
    return filteredInputBindings, filteredOutputBindings

def filter6(inputBindings, outputBindings, threshold):
    
    def filterByTreshold(bindings, activity):
        filteredBindings = [x for x in bindings if x[1]/activityCount[activity] > threshold]
        return filteredBindings
    
    def getMostFrequent(bindings):
        mostFrequentBinding = bindings[[x[1] for x in bindings].index(max([x[1] for x in bindings]))]
        return mostFrequentBinding
    
    
    def getSubsequentInputBidnings(mostFrequentBinding, activity):
        for obligation in mostFrequentBinding[0]:
            if obligation[0] in inputBindings.keys():
                possibleInputBindings = [x for x in inputBindings[obligation[0]] if (activity, obligation[1]) in [(y[0], y[1]) for y in x[0]]]
                mostFrequentBinding = getMostFrequent(possibleInputBindings)
                addToFilteredInputBindings(mostFrequentBinding, obligation[0])
                if activity in [x[0] for x in mostFrequentBinding[0] if (activity, obligation[1]) in [(y[0], y[1]) for y in mostFrequentBinding[0]]]:
                    possibleInputBindings.remove(mostFrequentBinding)
                    try:
                        mostFrequentBinding = getMostFrequent(possibleInputBindings)
                        addToFilteredOutputBindings(mostFrequentBinding, obligation[0])
                    except:
                        continue
                
    def addToFilteredOutputBindings(mostFrequentBinding, activity):
        if mostFrequentBinding not in filteredOutputBindings[activity]:
            filteredOutputBindings[activity].append(mostFrequentBinding)
            getSubsequentInputBidnings(mostFrequentBinding, activity)
            
            
    def getSubsequentOutputBidnings(mostFrequentBinding, activity):
        for obligation in mostFrequentBinding[0]:
            if obligation[0] in outputBindings.keys():
                print(obligation)
                possibleOutputBindings = [x for x in outputBindings[obligation[0]] if (activity, obligation[1]) in [(y[0], y[1]) for y in x[0]]]
                mostFrequentBinding = getMostFrequent(possibleOutputBindings)
                addToFilteredOutputBindings(mostFrequentBinding, obligation[0])
                if activity in [x[0] for x in mostFrequentBinding[0] if (activity, obligation[1]) in [(y[0], y[1]) for y in mostFrequentBinding[0]]]:
                    possibleOutputBindings.remove(mostFrequentBinding)
                    try:
                        mostFrequentBinding = getMostFrequent(possibleOutputBindings)
                        addToFilteredOutputBindings(mostFrequentBinding, obligation[0])
                    except:
                        continue
                
    def addToFilteredInputBindings(mostFrequentBinding, activity):
        if mostFrequentBinding not in filteredInputBindings[activity]:
            filteredInputBindings[activity].append(mostFrequentBinding)
            getSubsequentOutputBidnings(mostFrequentBinding, activity)
    
    filteredOutputBindings = {act : [] for act in outputBindings.keys()}
    filteredInputBindings = {act : [] for act in inputBindings.keys()}
    
    for act in filteredOutputBindings.keys():
        filteredBindings = filterByTreshold(outputBindings[act], act)
        for binding in filteredBindings:
            addToFilteredOutputBindings(binding, act)
    
    for act in filteredInputBindings.keys():
        filteredBindings = filterByTreshold(inputBindings[act], act)
        for binding in filteredBindings:
            addToFilteredInputBindings(binding, act)
            
    return filteredInputBindings, filteredOutputBindings
#%%

class SimpleOCCNet:
    def __init__(self, dependencyGraph, outputBindings, inputBindings, activityCount, relativeOccuranceThreshold = 0):
        self.dependencyGraph = dependencyGraph
        self.activities = list(dependencyGraph._node.keys())
        self.edges = dependencyGraph._succ
        self.relativeOccuranceThreshold = relativeOccuranceThreshold
        self.inputBindings, self.outputBindings = filter4(inputBindings, outputBindings, self.relativeOccuranceThreshold)
        self.objectTypes = {objectType for bindings in self.inputBindings.values() for binding in bindings for (_, objectType, _, _) in binding[0]}
        self.activityCount = activityCount
        self.emptyState = {act1:{act2:{obj:[] for obj in self.edges[act1][act2].keys()} for act2 in self.edges[act1].keys()} for act1 in self.activities}
        self.state = self.emptyState
#%%
relativeOccuranceThreshold = 0
occnet = SimpleOCCNet(dependencyGraph, outputBindings, inputBindings, activityCount, relativeOccuranceThreshold)

colorPalette = ('#1B9E77',
                '#D95F02',
                '#7570B3',
                '#E7298A',
                '#66A61E',
                '#E6AB02',
                '#A6761D',
                '#666666')

dimensions = {'parentNode_w':200,
              'parentNode_h':120,
              'activityNode_w':150,
              'activityNode_h':100,
              'obligationNode_w':16,
              'obligationNode_h':16,
              'dist_x':500,
              'dist_y':300,
              'additional_w':40,
              'additional_h':40}

nodeColor = '#FFFFFF'

edgeColor = '#FFFFFF'

#%%
class ParentNode:
    def __init__(self, activity, dependencyGraph, inputBindings, outputBindings, dimensions, activityPosition, inputObligationMax, outputObligationMax):
        self.activity = activity
        self.id = 'parent_' + activity.replace(" ", "_")
        self.width = dimensions['parentNode_w']
        self.height = dimensions['parentNode_h']
        self.pos_x = activityPosition[0] * dimensions['dist_x']
        self.pos_y = activityPosition[1] * dimensions['dist_y']
        if activity in inputBindings.keys():
            self.width += len(inputBindings[activity]) * dimensions['additional_w']
            self.pos_x -= len(inputBindings[activity]) * dimensions['additional_w']/2
        if activity in outputBindings.keys():
            self.width += len(outputBindings[activity]) * dimensions['additional_w']
            self.pos_x -= len(outputBindings[activity]) * dimensions['additional_w']/2
        self.height += max((0, max((inputObligationMax, outputObligationMax)) - 2)) * dimensions['additional_h']
        self.pos_y -= max((0, max((inputObligationMax, outputObligationMax)) - 2)) * dimensions['additional_h']/2
        self.maxRow = max((inputObligationMax, outputObligationMax))

class ActivityNode:
    def __init__(self, activity, objectColors, inputBindings, outputBindings, parentNode):
        self.activity = activity
        self.id = 'activity_' + activity.replace(" ", "_")
        self.objectTypes = set()
        if activity in inputBindings.keys():
            for i in inputBindings[activity]:
                for j in i[0]:
                    self.objectTypes.add(j[1])
        if activity in outputBindings.keys():
            for i in outputBindings[activity]:
                for j in i[0]:
                    self.objectTypes.add(j[1])
        self.objectTypes = list(self.objectTypes)
        self.colors = [objectColors[obj] for obj in self.objectTypes]
        #self.activityTypes = activityTypes[activity]
        if activity in inputBindings.keys():
            self.inputBindings = copy.deepcopy(inputBindings[activity])
        else:
            self.inputBindings = []
        if activity in outputBindings.keys():
            self.outputBindings = copy.deepcopy(outputBindings[activity])
        else:
            self.outputBindings = []
        self.width = dimensions['activityNode_w']
        self.height = dimensions['activityNode_h']
        self.pos_x = (parentNode.width - self.width) / 2 + len(self.inputBindings) * dimensions['additional_w'] / 2 - len(self.outputBindings) * dimensions['additional_w'] / 2 
        self.pos_y = (parentNode.height - self.height) / 2
        self.parent_id = parentNode.id
        if activity[0:6]=='START_':
            self.type = 'start'
        elif activity[0:4]=='END_':
            self.type = 'end'
        else:
            self.type = 'activity'

class ActivityNodeForVis:
    def __init__(self, activityNode):
        self.activity = activityNode.activity
        self.activityID = activityNode.activity.replace(' ', '_')
        self.id = activityNode.id
        self.type = activityNode.type
        self.pos_x = activityNode.pos_x
        self.pos_y = activityNode.pos_y
        self.parent_id = activityNode.parent_id
        self.objectTypes = activityNode.objectTypes

class InputNode:
    def __init__(self, activity, row, column, index, objectType, objectColors, parentNode, objectRange):
        self.activity = activity
        self.id = 'input_' + activity.replace(" ", "_") + '_' + str(row) + '_' + str(column)
        self.index = index
        self.objectType = objectType.replace(" ", "_")
        self.width = dimensions['obligationNode_w']
        self.height = dimensions['obligationNode_h']
        self.pos_x = (column + 0.5) * dimensions['additional_w']
        self.pos_y = (parentNode.height - self.height) / 2 - (parentNode.maxRow / 2 - row) * dimensions['additional_h']
        self.parent_id = parentNode.id
        self.object_min = str(objectRange[0])
        self.object_max = str(objectRange[1])
        if objectRange[1] == 1:
            self.radius = 50
        else:
            self.radius = 0

class OutputNode:
    def __init__(self, activity, row, column, index, objectType, objectColors, parentNode, objectRange):
        self.activity = activity
        self.id = 'output_' + activity.replace(" ", "_") + '_' + str(row) + '_' + str(column)
        self.index = index
        self.objectType = objectType.replace(" ", "_")
        self.width = dimensions['obligationNode_w']
        self.height = dimensions['obligationNode_h']
        self.pos_x = parentNode.width - (column + 1) * dimensions['additional_w']
        self.pos_y = (parentNode.height - self.height) / 2 - (parentNode.maxRow / 2 - row) * dimensions['additional_h']
        self.parent_id = parentNode.id
        self.object_min = str(objectRange[0])
        self.object_max = str(objectRange[1])
        if objectRange[1] == 1:
            self.radius = 50
        else:
            self.radius = 0

class ObligationEdge:
    def __init__(self, start_id, end_id):
        self.start_id = start_id
        self.end_id = end_id
        self.id = 'obl_edge_' + start_id + '_' + end_id

class BindingEdge:
    def __init__(self, start_id, end_id):
        self.start_id = start_id
        self.end_id = end_id
        self.id = 'bin_edge_' + start_id + '_' + end_id
        
class ActivityEdge:
    def __init__(self, start_id, end_id, start_activity, end_activity):
        self.start_id = start_id
        self.end_id = end_id
        self.id = 'bin_edge_' + start_id + '_' + end_id
        self.start_activity = start_activity
        self.end_activity = end_activity

#%%

graphTable = []
placedNodes = []
nodesToPlace = copy.deepcopy(list(occnet.dependencyGraph._adj.keys()))
index = 0
activityPosition = {}

while nodesToPlace:
    graphTable.append([])
    firstTry = False
    for node in list(nodesToPlace):
        succ = set(occnet.dependencyGraph._adj[node].keys())
        succ.discard(node)
        if succ <= set(placedNodes):
            if not succ.intersection(set(graphTable[index])):
                graphTable[index].append(node)
                nodesToPlace.remove(node)
                placedNodes.append(node)
                activityPosition[node] = (-index, len(graphTable[index])-1)
                firstTry = True
    if not firstTry:   
        for node in list(nodesToPlace):
            succ = set(occnet.dependencyGraph._adj[node].keys())
            succ.discard(node)
            if succ.intersection(set(placedNodes)):
                if not succ.intersection(set(graphTable[index])):
                    graphTable[index].append(node)
                    nodesToPlace.remove(node)
                    placedNodes.append(node)
                    activityPosition[node] = (-index, len(graphTable[index])-1)
                
    index += 1

objectColors = {list(occnet.objectTypes)[i]:colorPalette[i] for i in range(len(occnet.objectTypes))}

inputObligationPositions = {}
inputObligationColsToRowsDict = {}
inputObligationRowsToColsDict = {}
inputObligationMax = {}
inputObligationEdgeDict = {}

for activity, bindings in occnet.inputBindings.items():
    inputObligationPositions[activity] = {}
    inputObligationColsToRowsDict[activity] = {}
    inputObligationRowsToColsDict[activity] = {}
    inputObligationMax[activity] = 0
    inputObligationEdgeDict[activity] = {}
    rowDict = {}
    row = 0
    for pred, objectTypes in occnet.dependencyGraph._pred[activity].items():
        rowDict[pred] = {}
        for objectType in objectTypes.keys():
            rowDict[pred][objectType] = row
            if row > inputObligationMax[activity]:
                inputObligationMax[activity] = row
            row += 1
    
    column = 0
    for binding in bindings:
        inputObligationPositions[activity][tuple((tuple(binding[0]), binding[1]))] = {}
        for obligation in binding[0]:
            row = rowDict[obligation[0]][obligation[1]]
            inputObligationPositions[activity][tuple((tuple(binding[0]), binding[1]))][obligation] = {'row' : rowDict[obligation[0]][obligation[1]], 'column' : column}
            if column in inputObligationColsToRowsDict[activity].keys():
                inputObligationColsToRowsDict[activity][column].append(rowDict[obligation[0]][obligation[1]])
            else:
                inputObligationColsToRowsDict[activity][column] = [rowDict[obligation[0]][obligation[1]]]
            if rowDict[obligation[0]][obligation[1]] in inputObligationRowsToColsDict[activity].keys():
                inputObligationRowsToColsDict[activity][rowDict[obligation[0]][obligation[1]]].append(column)
            else:
                inputObligationRowsToColsDict[activity][rowDict[obligation[0]][obligation[1]]] = [column]
            if obligation[0] in inputObligationEdgeDict[activity].keys():
                if obligation[1] in inputObligationEdgeDict[activity][obligation[0]].keys():
                    inputObligationEdgeDict[activity][obligation[0]][obligation[1]].append((column, row))
                else:
                    inputObligationEdgeDict[activity][obligation[0]][obligation[1]] = [(column, row)]
            else:
                inputObligationEdgeDict[activity][obligation[0]] = {obligation[1]:[(column, row)]}
        column += 1

outputObligationPositions = {}
outputObligationColsToRowsDict = {}
outputObligationRowsToColsDict = {}
outputObligationMax = {}
outputObligationEdgeDict = {}

for activity, bindings in occnet.outputBindings.items():
    outputObligationPositions[activity] = {}
    outputObligationColsToRowsDict[activity] = {}
    outputObligationRowsToColsDict[activity] = {}
    outputObligationMax[activity] = 0
    outputObligationEdgeDict[activity] = {}
    rowDict = {}
    row = 0
    for succ, objectTypes in occnet.dependencyGraph._succ[activity].items():
        rowDict[succ] = {}
        for objectType in objectTypes.keys():
            rowDict[succ][objectType] = row
            if row > outputObligationMax[activity]:
                outputObligationMax[activity] = row
            row += 1
    column = 0
    for binding in bindings:
        outputObligationPositions[activity][tuple((tuple(binding[0]), binding[1]))] = {}
        for obligation in binding[0]:
            row = rowDict[obligation[0]][obligation[1]]
            outputObligationPositions[activity][tuple((tuple(binding[0]), binding[1]))][obligation] = {'row' : rowDict[obligation[0]][obligation[1]], 'column' : column}
            if column in outputObligationColsToRowsDict[activity].keys():
                outputObligationColsToRowsDict[activity][column].append(rowDict[obligation[0]][obligation[1]])
            else:
                outputObligationColsToRowsDict[activity][column] = [rowDict[obligation[0]][obligation[1]]]
            if rowDict[obligation[0]][obligation[1]] in outputObligationRowsToColsDict[activity].keys():
                outputObligationRowsToColsDict[activity][rowDict[obligation[0]][obligation[1]]].append(column)
            else:
                outputObligationRowsToColsDict[activity][rowDict[obligation[0]][obligation[1]]] = [column]
            if obligation[0] in outputObligationEdgeDict[activity].keys():
                if obligation[1] in outputObligationEdgeDict[activity][obligation[0]].keys():
                    outputObligationEdgeDict[activity][obligation[0]][obligation[1]].append((column, row))
                else:
                    outputObligationEdgeDict[activity][obligation[0]][obligation[1]] = [(column, row)]
            else:
                outputObligationEdgeDict[activity][obligation[0]] = {obligation[1]:[(column, row)]}
        column += 1
#%%
parentNodes = []
activityNodes = []
activityNodeForVis = []
inputNodes = []
outputNodes = []
obligationEdges = []
inputBindingEdges = []
outputBindingEdges = []
activityEdges = []

for activity in dependencyGraph._node.keys():
    if activity in occnet.inputBindings.keys():
        inputMax = inputObligationMax[activity]
    else:
        inputMax = 0
    if activity in occnet.outputBindings.keys():
        outputMax = outputObligationMax[activity]
    else:
        outputMax = 0
    parentNodes.append(ParentNode(activity, occnet.dependencyGraph, occnet.inputBindings, occnet.outputBindings, dimensions, activityPosition[activity], inputMax, outputMax))
    activityNodes.append(ActivityNode(activity, objectColors, occnet.inputBindings, occnet.outputBindings, parentNodes[-1]))
    activityNodeForVis.append(ActivityNodeForVis(activityNodes[-1]))
    if activity in occnet.inputBindings.keys():
        for binding in occnet.inputBindings[activity]:
            for obligation in binding[0]:
                row = inputObligationPositions[activity][tuple((tuple(binding[0]), binding[1]))][obligation]['row']
                column = inputObligationPositions[activity][tuple((tuple(binding[0]), binding[1]))][obligation]['column']
                inputNodes.append(InputNode(activity, row, column, obligation[2], obligation[1], objectColors, parentNodes[-1], obligation[3]))
    if activity in occnet.outputBindings.keys():
        for binding in occnet.outputBindings[activity]:
            for obligation in binding[0]:
                row = outputObligationPositions[activity][tuple((tuple(binding[0]), binding[1]))][obligation]['row']
                column = outputObligationPositions[activity][tuple((tuple(binding[0]), binding[1]))][obligation]['column']
                outputNodes.append(OutputNode(activity, row, column, obligation[2], obligation[1], objectColors, parentNodes[-1], obligation[3]))
    if activity in inputObligationColsToRowsDict.keys():
        for col, rows in inputObligationColsToRowsDict[activity].items():
            rows.sort()
            for row1, row2 in zip(rows, rows[1:]):
                obligationEdges.append(ObligationEdge('input_' + activity.replace(" ", "_") + '_' + str(row1) + '_' + str(col), 'input_' + activity.replace(" ", "_") + '_' + str(row2) + '_' + str(col)))
    if activity in outputObligationColsToRowsDict.keys():
        for col, rows in outputObligationColsToRowsDict[activity].items():
            rows.sort()
            for row1, row2 in zip(rows, rows[1:]):
                obligationEdges.append(ObligationEdge('output_' + activity.replace(" ", "_") + '_' + str(row1) + '_' + str(col), 'output_' + activity.replace(" ", "_") + '_' + str(row2) + '_' + str(col)))

outestInputDict = {}
for act1 in inputObligationEdgeDict.keys():
    outestInputDict[act1] = {}
    for act2 in inputObligationEdgeDict[act1].keys():
        outestInputDict[act1][act2] = {}
        for objectType in inputObligationEdgeDict[act1][act2].keys():
            outestInputDict[act1][act2][objectType] = False
            positions = inputObligationEdgeDict[act1][act2][objectType]
            positions = np.array(positions)
            positions = positions[positions[:,0].argsort()]
            outestInputDict[act1][act2][objectType] = positions[0]
            inputBindingEdges.append(BindingEdge('input_' + act1.replace(" ", "_") + '_' + str(positions[-1][1]) + '_' + str(positions[-1][0]), 'activity_' + act1.replace(" ", "_")))
            for position1, position2 in zip(positions, positions[1:]):
                inputBindingEdges.append(BindingEdge('input_' + act1.replace(" ", "_") + '_' + str(position1[1]) + '_' + str(position1[0]), 'input_' + act1.replace(" ", "_") + '_' + str(position2[1]) + '_' + str(position2[0])))

outestOutputDict = {}
for act1 in outputObligationEdgeDict.keys():
    outestOutputDict[act1] = {}
    for act2 in outputObligationEdgeDict[act1].keys():
        outestOutputDict[act1][act2] = {}
        for objectType in outputObligationEdgeDict[act1][act2].keys():
            outestOutputDict[act1][act2][objectType] = False
            positions = outputObligationEdgeDict[act1][act2][objectType]
            positions = np.array(positions)
            positions = positions[positions[:,0].argsort()[::1]]
            outestOutputDict[act1][act2][objectType] = positions[0]
            outputBindingEdges.append(BindingEdge('activity_' + act1.replace(" ", "_"), 'output_' + act1.replace(" ", "_") + '_' + str(positions[-1][1]) + '_' + str(positions[-1][0])))
            for position1, position2 in zip(positions, positions[1:]):
                outputBindingEdges.append(BindingEdge('output_' + act1.replace(" ", "_") + '_' + str(position2[1]) + '_' + str(position2[0]), 'output_' + act1.replace(" ", "_") + '_' + str(position1[1]) + '_' + str(position1[0])))


for act1 in outestOutputDict.keys():
    for act2 in outestOutputDict[act1].keys():
        for objectType in outestOutputDict[act1][act2].keys():
            activityEdges.append(ActivityEdge('output_' + act1.replace(" ", "_") + '_' + str(outestOutputDict[act1][act2][objectType][1]) + '_' + str(outestOutputDict[act1][act2][objectType][0]), 'input_' + act2.replace(" ", "_") + '_' + str(outestInputDict[act2][act1][objectType][1]) + '_' + str(outestInputDict[act2][act1][objectType][0]), act1, act2))

            

styles = 'html, \nbody, \n#root,\n.flow {\n height: 95%;\n width: 100%\n} \n.App {\n height: 100%;\n width: 100%\n} \n.App {\n font-family: sans-serif;\n text-align: center; \n} \n.react-flow__handle {\n opacity: 1;\n visibility: hidden\n}\n.container {font-size: 16pt; font-weight: bolder;}\n'
for node in activityNodes:
    percentiles = np.linspace(0,100,len(node.colors)+1)
    styleStart = '.' + node.id +' {background-image: linear-gradient('
    styleEnd = ');} \n'
    styleMiddle = [str(node.colors[i]) + ' ' + str(percentiles[i]) + '%, '
                      + str(node.colors[i]) + ' ' + str(percentiles[i+1]) + '%, '
                      for i in range(len(node.colors))]
    styleMiddle = ''.join(styleMiddle)
    styleMiddle = styleMiddle[:-2]
    style = styleStart + styleMiddle + styleEnd
    styles = styles + style
for objectType in occnet.objectTypes:
    style = '.' + objectType.replace(" ", "_") + ' {background: ' + objectColors[objectType] + '}\n'
    styles = styles + style
#%%
with open('C:/Users/Caspar Mensing/occn-visualization/src/obligationEdges.json', 'w') as f:
    json.dump([ob.__dict__ for ob in obligationEdges], f)
with open('C:/Users/Caspar Mensing/occn-visualization/src/inputBindingEdges.json', 'w') as f:
    json.dump([ob.__dict__ for ob in inputBindingEdges], f)
with open('C:/Users/Caspar Mensing/occn-visualization/src/outputBindingEdges.json', 'w') as f:
    json.dump([ob.__dict__ for ob in outputBindingEdges], f)
with open('C:/Users/Caspar Mensing/occn-visualization/src/activityEdges.json', 'w') as f:
    json.dump([ob.__dict__ for ob in activityEdges], f)
with open('C:/Users/Caspar Mensing/occn-visualization/src/outputNodes.json', 'w') as f:
    json.dump([ob.__dict__ for ob in outputNodes], f)
with open('C:/Users/Caspar Mensing/occn-visualization/src/inputNodes.json', 'w') as f:
    json.dump([ob.__dict__ for ob in inputNodes], f)
with open('C:/Users/Caspar Mensing/occn-visualization/src/activityNodes.json', 'w') as f:
    json.dump([ob.__dict__ for ob in activityNodeForVis], f)
with open('C:/Users/Caspar Mensing/occn-visualization/src/parentNodes.json', 'w') as f:
    json.dump([ob.__dict__ for ob in parentNodes], f)
with open('C:/Users/Caspar Mensing/occn-visualization/src/styles.css', 'w') as f:
    f.write(styles)