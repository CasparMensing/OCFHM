# -*- coding: utf-8 -*-
"""
Created on Wed Jun 19 10:25:58 2024

@author: Caspar Mensing
"""

from ocpa.objects.log.importer.ocel import factory as ocel1_import_factory
from ocpa.objects.log.importer.ocel2.sqlite import factory as ocel2_sqlite_import_factory
from ocpa.objects.log.importer.ocel2.xml import factory as ocel2_xml_import_factory
import pandas as pd
import pm4py
import networkx as nx
import copy
import itertools
from collections import Counter
import pickle
import time
import csv
import scipy
import os
import numpy as np
import json
from pynpm import NPMPackage
#%%

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

def loadOCEventLog(filePath, fileExtension, ocelVersion, objectList = []):
    print(objectList)
    if ocelVersion == 1:
        if fileExtension == '.jsonocel':
            ocel = ocel1_import_factory.apply(filePath + fileExtension)
        else:
            raise ValueError('Unknown file extension for this OCEL version.')
    elif ocelVersion == 2:
        if fileExtension == '.xml':
            ocel = ocel2_xml_import_factory.apply(filePath + fileExtension)
        elif fileExtension == '.sqlite':
            ocel = ocel2_sqlite_import_factory.apply(filePath + fileExtension)
        else:
            raise ValueError('Unknown file extension for this OCEL version.')
    else:
        raise ValueError('Unknown OCEL version. Use 1 for OCEL 1.0 or 2 for OCEL 2.0.')
    objectTypes = ocel.object_types
    if not set(objectList) <= set(objectTypes):
        raise ValueError('The provided object types are not part of the provided OCEL')
    columnsList = ['event_id', 'event_activity', 'event_timestamp']
    if objectList:
        columnsList.extend(objectList)
    else:
        columnsList.extend(objectTypes)
    eventLog = ocel.log.log.copy(deep = True)[columnsList].replace('', None)
    if objectList:
        eventLog = eventLog[eventLog[objectList].T.any()]
        objectTypes = objectList
    return ocel, objectTypes, eventLog

def generateEventLogForMiner(eventLog, objectTypes):
    columnsList = ['event_activity', 'event_timestamp', 'event_id']
    columnsList.extend(objectTypes)
    eventLogForMiner = eventLog[columnsList].melt(['event_activity', 'event_timestamp', 'event_id'], value_name='object', var_name='object_type').explode('object').dropna()
    eventLogForMiner = eventLogForMiner[['event_activity', 'event_timestamp', 'object', 'object_type', 'event_id']]
    eventLogForMiner = eventLogForMiner.sort_values('event_timestamp', ignore_index = True)
    return eventLogForMiner

def generateEventLogDict(eventLogForMiner):
    eventLogDict = {k: v for k, v in eventLogForMiner.groupby('object')}
    return eventLogDict

def mineHeuNets(eventLogForMiner, objectTypes, dependency_threshold = 0.5, and_threshold = 0.65, loop_two_threshold = 0.5,  min_act_count = 1, min_dfg_occurrences = 1):
    heuNets = {}
    for objType in objectTypes:
        #if objType == 'orders':
        #    heu_net = pm4py.discovery.discover_heuristics_net(eventLogForMiner[eventLogForMiner['object_type'] == objType][['case:concept:name', 'concept:name', 'time:timestamp']],
        #                                                  0.6, 1, 1)
        #else:
        #    heu_net = pm4py.discovery.discover_heuristics_net(eventLogForMiner[eventLogForMiner['object_type'] == objType][['case:concept:name', 'concept:name', 'time:timestamp']],
        #                                                  dependency_threshold, and_threshold, loop_two_threshold)
        heu_net = pm4py.discovery.discover_heuristics_net(eventLogForMiner[eventLogForMiner['object_type'] == objType][['case:concept:name', 'concept:name', 'time:timestamp']],
                                                          dependency_threshold, and_threshold, loop_two_threshold)
        heuNets[objType] = heu_net
    return heuNets

def getEvents(heuNets):
    events=set()
    events.update(*[net.activities for net in heuNets.values()])
    return(events)

def generateDependencyDict(heuNets, objectTypes, ev, inconsumableObjects = [], inconsumableThreshold = 1):
    evToEvDict = {act:{} for act in ev}
    startActivities = dict()
    endActivities = dict()
    for objectType, net in heuNets.items():
        if objectType not in inconsumableObjects:
            for act1, node1 in net.nodes.items():
                for node2, edge in node1.output_connections.items():
                    act2 = node2.node_name
                    dependencyValue = edge[0].dependency_value
                    if act2 in evToEvDict[act1].keys():
                        evToEvDict[act1][act2][objectType] = {'dependenceMeasure':dependencyValue, 'objectType':objectType}
                    else:
                        evToEvDict[act1][act2] = {objectType: {'dependenceMeasure':dependencyValue, 'objectType':objectType}}
                for startActivity, count in net.start_activities[0].items():
                    if objectType in startActivities.keys():
                        startActivities[objectType][startActivity] = ('START_' + objectType, count)
                    else:
                        startActivities[objectType] = {startActivity : ('START_' + objectType, count)}
                    if 'START_' + objectType in evToEvDict.keys():
                        evToEvDict['START_' + objectType][startActivity] = {objectType:{'dependenceMeasure':count/(count+1), 'objectType':objectType}}
                    else:
                        evToEvDict['START_' + objectType] = {startActivity:{objectType:{'dependenceMeasure':count/(count+1), 'objectType':objectType}}}
                for endActivity, count in net.end_activities[0].items():
                    if objectType in endActivities.keys():
                        endActivities[objectType][endActivity] = ('END_' + objectType, count)
                    else:
                        endActivities[objectType] = {endActivity : ('END_' + objectType, count)}
                    if endActivity in evToEvDict.keys():
                        evToEvDict[endActivity]['END_' + objectType] = {objectType:{'dependenceMeasure':count/(count+1), 'objectType':objectType}}
                    else:
                        evToEvDict[endActivity] = {'END_' + objectType:{objectType:{'dependenceMeasure':count/(count+1), 'objectType':objectType}}}
        else:
            print(objectType)
            for key, value in net.dfg_window_2_matrix.items():
                for key2, value2 in value.items():
                    if value2 >= inconsumableThreshold:
                        if key2 in evToEvDict[key].keys():
                            evToEvDict[key][key2][objectType] = {'occurance':value2, 'objectType':objectType}
                            print('++++++++')
                            print(key)
                            print(key2)
                        else:
                            evToEvDict[key][key2] = {objectType:{'occurance':value2, 'objectType':objectType}}
                            print('++++++++')
                            print(key)
                            print(key2)
                for startActivity, count in net.start_activities[0].items():
                    if objectType in startActivities.keys():
                        startActivities[objectType][startActivity] = ('START_' + objectType, count)
                    else:
                        startActivities[objectType] = {startActivity : ('START_' + objectType, count)}
                    if 'START_' + objectType in evToEvDict.keys():
                        evToEvDict['START_' + objectType][startActivity] = {objectType:{'dependenceMeasure':count/(count+1), 'objectType':objectType}}
                    else:
                        evToEvDict['START_' + objectType] = {startActivity:{objectType:{'dependenceMeasure':count/(count+1), 'objectType':objectType}}}
                for endActivity, count in net.end_activities[0].items():
                    if objectType in endActivities.keys():
                        endActivities[objectType][endActivity] = ('END_' + objectType, count)
                    else:
                        endActivities[objectType] = {endActivity : ('END_' + objectType, count)}
                    if endActivity in evToEvDict.keys():
                        evToEvDict[endActivity]['END_' + objectType] = {objectType:{'dependenceMeasure':count/(count+1), 'objectType':objectType}}
                    else:
                        evToEvDict[endActivity] = {'END_' + objectType:{objectType:{'dependenceMeasure':count/(count+1), 'objectType':objectType}}}
    return evToEvDict, startActivities, endActivities

def generateDependencyGraph(evToEvDict):
    dependencyGraph = nx.MultiDiGraph(evToEvDict)
    return dependencyGraph

def getPredecessors(ev, predecessorDict):
    predecessors = []
    for activity in ev:
        for pred, ots in predecessorDict[activity].items():
            for ot in ots.keys():
                predecessors.append([activity, ot, pred])
    predecessors = pd.DataFrame(predecessors, columns = ['activity', 'object_type', 'predecessors'])
    return predecessors

def getSuccessors(ev, successorDict):
    successors = []
    for activity in ev:
        for succ, ots in successorDict[activity].items():
            for ot in ots.keys():
                successors.append([activity, ot, succ])
    successors = pd.DataFrame(successors, columns = ['activity', 'object_type', 'successors'])
    return successors

def getClosestPredecessor(log, position, activity, activityList, objectType, predecessors):
    if position == 0:
        return None, None
    else:
        if len(predecessors) == 0:
            return None, None
        else:
            for i in range(position-1, -1, -1):
                if activityList[i] in predecessors:
                    return activityList[i], i
            return None, None

def getClosestSuccessor(log, position, activity, activityList, objectType, successors):
    if position == len(log)-1:
        return None, None
    
    else:
        if len(successors) == 0:
            return None, None
        else:
            for i in range(position+1, len(log)):
                if activityList.iloc[i] in successors:
                    return activityList.iloc[i], i
            return None, None
        
def generateClosestPredecessorDF(objectSet, eventLogDict, predecessors):
    closestPredecessorList = []
    predecessorActObjDict = {k: v['predecessors'].to_list() for k, v in predecessors.groupby(['activity', 'object_type'])}
    predecessorActObjDictDefault = []
    for objectID in objectSet:
        uniqueLogSnippet = eventLogDict[objectID]
        activityList = uniqueLogSnippet['event_activity'].to_list()
        for i in range(len(uniqueLogSnippet)):
            activity = activityList[i]
            objectType = uniqueLogSnippet['object_type'].iloc[0]
            event_id = uniqueLogSnippet['event_id'].iloc[i]
            closestPredecessor, index = getClosestPredecessor(uniqueLogSnippet, i, activity, activityList, objectType, predecessorActObjDict.get((activity, objectType), predecessorActObjDictDefault))
            if index is not None:
                closestPredecessorID = uniqueLogSnippet['event_id'].iloc[index]
            else:
                closestPredecessorID = None
            closestPredecessorTuple = (activity, event_id, closestPredecessor, closestPredecessorID, objectType, objectID)
            closestPredecessorList.append(closestPredecessorTuple)
    closestPredecessorDF = pd.DataFrame(closestPredecessorList, columns=['event_activity', 'event_id', 'predecessor', 'predecessor_event_id', 'object_type', 'object'])
    return closestPredecessorDF

def generateClosestSuccessorDF(objectSet, eventLogDict, successors):
    closestSuccessorList = []
    successorActObjDict = {k: v['successors'].to_list() for k, v in successors.groupby(['activity', 'object_type'])}
    successorActObjDictDefault = []
    for objectID in objectSet:
        uniqueLogSnippet = eventLogDict[objectID]
        #activityList = uniqueLogSnippet['event_activity'].to_list()
        for i in range(len(uniqueLogSnippet)):
            activity = uniqueLogSnippet['event_activity'].iloc[i]
            objectType = uniqueLogSnippet['object_type'].iloc[0]
            event_id = uniqueLogSnippet['event_id'].iloc[i]
            closestSuccessor, index = getClosestSuccessor(uniqueLogSnippet, i, activity, uniqueLogSnippet['event_activity'], objectType, successorActObjDict.get((activity, objectType), successorActObjDictDefault))
            if index is not None:
                closestSuccessorID = uniqueLogSnippet['event_id'].iloc[index]
            else:
                closestSuccessorID = None
            closestSuccessorTuple = (activity, event_id, closestSuccessor, closestSuccessorID, objectType, objectID)
            closestSuccessorList.append(closestSuccessorTuple)
    closestSuccessorDF = pd.DataFrame(closestSuccessorList, columns=['event_activity', 'event_id', 'successor', 'successor_event_id', 'object_type', 'object'])
    return closestSuccessorDF

def sorted_k_partitions(seq, k):
    """Returns a list of all unique k-partitions of `seq`.

    Each partition is a list of parts, and each part is a tuple.

    The parts in each individual partition will be sorted in shortlex
    order (i.e., by length first, then lexicographically).

    The overall list of partitions will then be sorted by the length
    of their first part, the length of their second part, ...,
    the length of their last part, and then lexicographically.
    """
    n = len(seq)
    groups = []  # a list of lists, currently empty

    def generate_partitions(i):
        if i >= n:
            yield list(map(tuple, groups))
        else:
            if n - i > k - len(groups):
                for group in groups:
                    group.append(seq[i])
                    yield from generate_partitions(i + 1)
                    group.pop()

            if len(groups) < k:
                groups.append([seq[i]])
                yield from generate_partitions(i + 1)
                groups.pop()

    result = generate_partitions(0)

    # Sort the parts in each partition in shortlex order
    result = [sorted(ps, key = lambda p: (len(p), p)) for ps in result]
    # Sort partitions by the length of each part, then lexicographically.
    result = sorted(result, key = lambda ps: (*map(len, ps), ps))

    return result

def mineOutputBindings(eventIDSet, eventToActivityDict, closestPredecessorDF, events, startActivities, dependencyDict, eventLogForMiner, combo_threshold=1000):
    outputBindingList = []
    skippedEvents = []
    eventCounter = 1
    eventLen = len(eventIDSet)
    timerDict = {
        'snippet':0,
        'allEventObjects':0,
        'succSet':0,
        'objSet':0,
        'global':0
        }
    global_start_time = time.time()
    closestPredecessorDict = {k: v for k, v in closestPredecessorDF.groupby('predecessor_event_id')}
    defaultClosestPredecessorDict = pd.DataFrame(data=None, columns=closestPredecessorDF.columns)
    eventLogForMinerDict = {k: v for k, v in eventLogForMiner.groupby('event_id')}
    defaultEventLogForMinerDict = pd.DataFrame(data=None, columns=eventLogForMiner.columns)
    for event in eventIDSet:
        print('event ' + str(event) + ' , ' + str(eventCounter) + ' of ' + str(eventLen))
        tooManyCombinations = False
        activity = eventToActivityDict[event]
        start_time = time.time()
        snippet = closestPredecessorDict.get(event, defaultClosestPredecessorDict)
        #return snippet
        snippetObjectTypeDict = {k: v['event_id'] for k, v in snippet.groupby('object_type')}
        defaultSnippetObjectTypeDict = pd.DataFrame(data=None, columns=snippet.columns)['event_id']
        snippetObjectTypeEventIDDict = {k: v['object'] for k, v in snippet.groupby(['object_type', 'event_id'])}
        defaultSnippetObjectTypeEventIDDict = pd.DataFrame(data=None, columns=snippet.columns)['object']
        snippet_time = time.time()
        timerDict['snippet'] += snippet_time - start_time
        binding = [event, activity, dict()]
        allCombinations = [event, activity, dict()]
        start_time = time.time()
        allEventObjects = eventLogForMinerDict.get(event, defaultEventLogForMinerDict)[['object_type', 'object']].values
        allEventObjects_time = time.time()
        timerDict['allEventObjects'] += allEventObjects_time - start_time
        allObjectTypes = set(allEventObjects[:,0])
        allObjectsDict = {objectType:[] for objectType in allObjectTypes}
        for i in allEventObjects:
            allObjectsDict[i[0]].append(i[1])
        for objType in allObjectTypes:
            binding[2][objType] = []
            allCombinations[2][objType] = []
            start_time = time.time()
            succSet = set(snippetObjectTypeDict.get(objType, defaultSnippetObjectTypeDict))
            succSet_time = time.time()
            timerDict['succSet'] += succSet_time - start_time
            for succ in succSet:
                succActivity = eventToActivityDict[succ]
                start_time = time.time()
                objSet = frozenset(snippetObjectTypeEventIDDict.get((objType, succ), defaultSnippetObjectTypeEventIDDict))
                objSet_time = time.time()
                timerDict['objSet'] += objSet_time - start_time
                for obj in objSet:
                    try:
                        allObjectsDict[objType].remove(obj)
                    except ValueError:
                        pass
                obligation = [succActivity, objType, len(objSet), objSet]
                binding[2][objType].append(obligation)
            if allObjectsDict[objType]:
                if activity in dependencyDict.keys():
                    if 'END_' + objType in dependencyDict[activity].keys():
                        obligation = ['END_' + objType, objType, len(allObjectsDict[objType]), frozenset(allObjectsDict[objType])]
                        binding[2][objType].append(obligation)
            seq = copy.deepcopy(binding[2][objType])
            foundPartition = False
            totalCombinations = 0
            for k in range(len(seq)+1):
                totalCombinations += scipy.special.stirling2(len(seq), k)
                if totalCombinations > combo_threshold:
                    print('Too many possibilities for outputbindings. Skipped event ' + str(event))
                    skippedEvents.append(event)
                    tooManyCombinations = True
                    break
                for groups in sorted_k_partitions(seq, k):
                    if all( len({x for xs in group for x in xs[3]}) == len([x for xs in group for x in xs[3]]) for group in groups):
                        #allCombinations[2][objType].append((k, groups))
                        allCombinations[2][objType].append(copy.deepcopy(groups))
                        foundPartition = True
                if foundPartition:
                    break
            for i in allCombinations[2][objType]:
                indexID = 0
                for j in i:
                    for k in j:
                        k[3] = indexID
                    indexID += 1
        if not tooManyCombinations:
            outputBindingList.append(allCombinations)
        eventCounter += 1
    allOutputBindings = []
    global_end_time = time.time()
    timerDict['global'] += global_end_time - global_start_time
    print('outputBindingList completed')
    for event in outputBindingList:
        act_of_marker = event[1]
        set_of_markers = []
        for objType, list_of_subgroups in event[2].items():
            set_of_markers.append([])
            for subgroup in list_of_subgroups:
                markers = []
                for object_set in subgroup:
                    object_set_as_tuples = [tuple(x) for x in object_set]
                    object_counter = Counter(object_set_as_tuples)
                    markers.extend(tuple([m[0], m[1], m[2]*object_counter[m], m[3]]) for m in object_counter)
                set_of_markers[-1].append(markers)
                #set_of_markers.append(2)
        combinations_of_markers = list(itertools.product(*set_of_markers))
        for combo in combinations_of_markers:
            allOutputBindings.append((act_of_marker, frozenset([tuple(x) for xs in combo for x in xs])))
    outputBindingsSingleCounts = Counter(allOutputBindings)
    print('allOutputBindings completed')
    outputBindingsRanges = {}
    outputBindingsRangesCounts = Counter()
    for binding in outputBindingsSingleCounts:
        key = (binding[0], frozenset((act, objType, index) for act, objType, _, index in binding[1]))
        if key in outputBindingsRanges.keys():
            outputBindingsRanges[key].append(tuple({(act, objType) : count} for act, objType, count, _ in binding[1]))
        else:
            outputBindingsRanges[key] = [tuple({(act, objType) : count} for act, objType, count, _ in binding[1])]
    print('outputBindingsRanges completed')
    outputBindingsRanges2 = {}
    for key, value in outputBindingsRanges.items():
        outputBindingsRanges2[key] = dict()
        for tupleOfDicts in value:
            for dict1 in tupleOfDicts:
                for key2, value2 in dict1.items():
                    if key2 in outputBindingsRanges2[key].keys():
                        if value2 < outputBindingsRanges2[key][key2][0]:
                            outputBindingsRanges2[key][key2][0] = value2
                        if value2 > outputBindingsRanges2[key][key2][1]:
                            outputBindingsRanges2[key][key2][1] = value2
                    else:
                        outputBindingsRanges2[key][key2] = [value2, value2]
    print('outputBindingsRanges2 completed')
    for binding in outputBindingsSingleCounts:
        key = (binding[0], frozenset((act, objType, index) for act, objType, _, index in binding[1]))
        value = outputBindingsSingleCounts[binding]
        outputBindingsRangesCounts.update({key: value})
    print('outputBindingsRangesCounts completed')
    outputBindings = {act : [] for act in events}
    for key in outputBindingsRanges2.keys():
        value = []
        count = outputBindingsRangesCounts[key]
        for i in range(len(key[1])):
            act, objType, index = list(key[1])[i]
            rangeTuple = tuple(outputBindingsRanges2[key][(act, objType)])
            value.append((act, objType, index, rangeTuple))
        binding = (value, count)
        outputBindings[key[0]].append(binding)
    print('outputBindings completed')
    for objectType, activityDict in startActivities.items():
        for activity, (startActivity, count) in activityDict.items():
            if startActivity in outputBindings.keys():
                outputBindings[startActivity].append(([(activity, objectType, 0, (1, float('inf')))], count))
            else:
                outputBindings[startActivity] = [([(activity, objectType, 0, (1, float('inf')))], count)]
    '''
    for objectType, activityDict in endActivities.items():
        for activity, (endActivity, count) in activityDict.items():
            if activity in outputBindings.keys():
                outputBindings[activity].append(([(endActivity, objectType, 0, (1, float('inf')))], count))
            else:
                outputBindings[activity] = [([(endActivity, objectType, 0, (1, float('inf')))], count)]
    '''
    return outputBindings, timerDict, skippedEvents

def mineInputBindings(eventIDSet, eventToActivityDict, closestSuccessorDF, events, endActivities, dependencyDict, eventLogForMiner, combo_threshold=1000):
    inputBindingList = []
    skippedEvents = []
    eventCounter = 1
    eventLen = len(eventIDSet)
    closestSuccessorDict = {k: v for k, v in closestSuccessorDF.groupby('successor_event_id')}
    defaultClosestSuccessorDict = pd.DataFrame(data=None, columns=closestSuccessorDF.columns)
    eventLogForMinerDict = {k: v for k, v in eventLogForMiner.groupby('event_id')}
    defaultEventLogForMinerDict = pd.DataFrame(data=None, columns=eventLogForMiner.columns)
    for event in eventIDSet:
        print('event ' + str(event) + ' , ' + str(eventCounter) + ' of ' + str(eventLen))
        tooManyCombinations = False
        activity = eventToActivityDict[event]
        snippet = closestSuccessorDict.get(event, defaultClosestSuccessorDict)
        snippetObjectTypeDict = {k: v['event_activity'] for k, v in snippet.groupby('object_type')}
        defaultSnippetObjectTypeDict = pd.DataFrame(data=None, columns=snippet.columns)['event_id']
        snippetObjectTypeEventIDDict = {k: v['object'] for k, v in snippet.groupby(['object_type', 'event_activity'])}
        defaultSnippetObjectTypeEventIDDict = pd.DataFrame(data=None, columns=snippet.columns)['object']
        binding = [event, activity, dict()]
        allCombinations = [event, activity, dict()]
        allEventObjects = eventLogForMinerDict.get(event, defaultEventLogForMinerDict)[['object_type', 'object']].values
        allObjectTypes = set(allEventObjects[:,0])
        allObjectsDict = {objectType:[] for objectType in allObjectTypes}
        for i in allEventObjects:
            allObjectsDict[i[0]].append(i[1])
        for objType in allObjectTypes:
            binding[2][objType] = []
            allCombinations[2][objType] = []
            predSet = set(snippetObjectTypeDict.get(objType, defaultSnippetObjectTypeDict))
            for pred in predSet:
                #predActivity = eventToActivityDict[pred]
                objSet = frozenset(snippetObjectTypeEventIDDict.get((objType, pred), defaultSnippetObjectTypeEventIDDict))
                for obj in objSet:
                    try:
                        allObjectsDict[objType].remove(obj)
                    except ValueError:
                        pass
                obligation = [pred, objType, len(objSet), objSet]
                binding[2][objType].append(obligation)
            if 'START_' + objType in dependencyDict.keys():
                if activity in dependencyDict['START_' + objType].keys():
                    if allObjectsDict[objType]:
                        obligation = ['START_' + objType, objType, len(allObjectsDict[objType]), frozenset(allObjectsDict[objType])]
                        binding[2][objType].append(obligation)
            seq = copy.deepcopy(binding[2][objType])
            foundPartition = False
            totalCombinations = 0
            for k in range(len(seq)+1):
                totalCombinations += scipy.special.stirling2(len(seq), k)
                if totalCombinations > combo_threshold:
                    print('Too many possibilities for outputbindings. Skipped event ' + str(event))
                    skippedEvents.append(event)
                    tooManyCombinations = True
                    break
                for groups in sorted_k_partitions(seq, k):
                    if all( len({x for xs in group for x in xs[3]}) == len([x for xs in group for x in xs[3]]) for group in groups):
                        allCombinations[2][objType].append(copy.deepcopy(groups))
                        foundPartition = True
                if foundPartition:
                    break
            for i in allCombinations[2][objType]:
                indexID = 0
                for j in i:
                    for k in j:
                        k[3] = indexID
                    indexID += 1
        if not tooManyCombinations:
            inputBindingList.append(allCombinations)
        eventCounter += 1
    allInputBindings = []
    for event in inputBindingList:
        act_of_marker = event[1]
        set_of_markers = []
        for objType, list_of_subgroups in event[2].items():
            set_of_markers.append([])
            for subgroup in list_of_subgroups:
                markers = []
                for object_set in subgroup:
                    object_set_as_tuples = [tuple(x) for x in object_set]
                    object_counter = Counter(object_set_as_tuples)
                    markers.extend(tuple([m[0], m[1], m[2]*object_counter[m], m[3]]) for m in object_counter)
                set_of_markers[-1].append(markers)
                #set_of_markers.append(2)
        combinations_of_markers = list(itertools.product(*set_of_markers))
        for combo in combinations_of_markers:
            allInputBindings.append((act_of_marker, frozenset([tuple(x) for xs in combo for x in xs])))
    inputBindingsSingleCounts = Counter(allInputBindings)
    inputBindingsRanges = {}
    inputBindingsRangesCounts = Counter()
    
    for binding in inputBindingsSingleCounts:
        key = (binding[0], frozenset((act, objType, index) for act, objType, _, index in binding[1]))
        if key in inputBindingsRanges.keys():
            inputBindingsRanges[key].append(tuple({(act, objType) : count} for act, objType, count, _ in binding[1]))
        else:
            inputBindingsRanges[key] = [tuple({(act, objType) : count} for act, objType, count, _ in binding[1])]
    inputBindingsRanges2 = {}
    for key, value in inputBindingsRanges.items():
        inputBindingsRanges2[key] = dict()
        for tupleOfDicts in value:
            for dict1 in tupleOfDicts:
                for key2, value2 in dict1.items():
                    if key2 in inputBindingsRanges2[key].keys():
                        if value2 < inputBindingsRanges2[key][key2][0]:
                            inputBindingsRanges2[key][key2][0] = value2
                        if value2 > inputBindingsRanges2[key][key2][1]:
                            inputBindingsRanges2[key][key2][1] = value2
                    else:
                        inputBindingsRanges2[key][key2] = [value2, value2]
    
    for binding in inputBindingsSingleCounts:
        key = (binding[0], frozenset((act, objType, index) for act, objType, _, index in binding[1]))
        value = inputBindingsSingleCounts[binding]
        inputBindingsRangesCounts.update({key: value})
        
    inputBindings = {act : [] for act in events}
    for key in inputBindingsRanges2.keys():
        value = []
        count = inputBindingsRangesCounts[key]
        for i in range(len(key[1])):
            act, objType, index = list(key[1])[i]
            rangeTuple = tuple(inputBindingsRanges2[key][(act, objType)])
            value.append((act, objType, index, rangeTuple))
        binding = (value, count)
        inputBindings[key[0]].append(binding)
    '''
    for objectType, activityDict in startActivities.items():
        for activity, (startActivity, count) in activityDict.items():
            if activity in inputBindings.keys():
                inputBindings[activity].append(([(startActivity, objectType, 0, (1, float('inf')))], count))
            else:
                outputBindings[activity] = [([(startActivity, objectType, 0, (1, float('inf')))], count)]
    '''
    for objectType, activityDict in endActivities.items():
        for activity, (endActivity, count) in activityDict.items():
            if endActivity in inputBindings.keys():
                inputBindings[endActivity].append(([(activity, objectType, 0, (1, float('inf')))], count))
            else:
                inputBindings[endActivity] = [([(activity, objectType, 0, (1, float('inf')))], count)]
    return inputBindings, skippedEvents

def generateActivityCount(eventLog, startActivities, endActivities):
    activityCount = Counter(eventLog['event_activity'])
    for objectType, activityDict in startActivities.items():
        for activity, (startActivity, count) in activityDict.items():
            activityCount[startActivity] += count
    for objectType, activityDict in endActivities.items():
        for activity, (endActivity, count) in activityDict.items():
            activityCount[endActivity] += count
    return activityCount

def filter4(inputBindings, outputBindings, threshold, activityCount):
    
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

def visualizer(dependencyGraph, outputBindings, inputBindings, activityCount, relativeOccuranceThreshold, vizFilePath):
    occnet = SimpleOCCNet(dependencyGraph, outputBindings, inputBindings, activityCount, relativeOccuranceThreshold)
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
    with open(vizFilePath + '/src/obligationEdges.json', 'w') as f:
        json.dump([ob.__dict__ for ob in obligationEdges], f)
    with open(vizFilePath + '/src/inputBindingEdges.json', 'w') as f:
        json.dump([ob.__dict__ for ob in inputBindingEdges], f)
    with open(vizFilePath + '/src/outputBindingEdges.json', 'w') as f:
        json.dump([ob.__dict__ for ob in outputBindingEdges], f)
    with open(vizFilePath + '/src/activityEdges.json', 'w') as f:
        json.dump([ob.__dict__ for ob in activityEdges], f)
    with open(vizFilePath + '/src/outputNodes.json', 'w') as f:
        json.dump([ob.__dict__ for ob in outputNodes], f)
    with open(vizFilePath + '/src/inputNodes.json', 'w') as f:
        json.dump([ob.__dict__ for ob in inputNodes], f)
    with open(vizFilePath + '/src/activityNodes.json', 'w') as f:
        json.dump([ob.__dict__ for ob in activityNodeForVis], f)
    with open(vizFilePath + '/src/parentNodes.json', 'w') as f:
        json.dump([ob.__dict__ for ob in parentNodes], f)
    with open(vizFilePath + '/src/styles.css', 'w') as f:
        f.write(styles)
    pkg = NPMPackage(vizFilePath + '/package.json', shell = True)
    pkg.run_script('dev')

class SimpleOCCNet:
    def __init__(self, dependencyGraph, outputBindings, inputBindings, activityCount, relativeOccuranceThreshold = 0):
        self.dependencyGraph = dependencyGraph
        self.activities = list(dependencyGraph._node.keys())
        self.edges = dependencyGraph._succ
        self.relativeOccuranceThreshold = relativeOccuranceThreshold
        self.inputBindings, self.outputBindings = filter4(inputBindings, outputBindings, self.relativeOccuranceThreshold, activityCount)
        self.objectTypes = {objectType for bindings in self.inputBindings.values() for binding in bindings for (_, objectType, _, _) in binding[0]}
        self.activityCount = activityCount
        self.emptyState = {act1:{act2:{obj:[] for obj in self.edges[act1][act2].keys()} for act2 in self.edges[act1].keys()} for act1 in self.activities}
        self.state = self.emptyState

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
def main():
    print('+++++++++++++++++++++++++++++++++++++++')
    print('Object-Centric Flexible Heuristic Miner')
    print('+++++++++++++++++++++++++++++++++++++++')
    userPath = input('Absolute filepath to object-centric event log (or simply drag-and-drop file): ').strip('"')
    print(userPath)
    filePath, fileExtension = os.path.splitext(userPath)
    fileName = os.path.splitext(os.path.basename(userPath))[0]
    print(filePath)
    print(fileName)
    print(fileExtension)
    ocelVersion = int(input('OCEL version (1 or 2): '))
    print(ocelVersion)
    dependency_threshold = float(input('Dependency- and loop-1-threshold: '))
    print(dependency_threshold)
    and_threshold = 0.65
    loop_two_threshold = float(input('Loop-2-threshold: '))
    combo_threshold = 1000#int(input('Maximal number of groups per event: '))
    objectList = input('Comma-sperated list of objects to include in the mining process (leave empty to include all): ')
    print(objectList)
    if objectList:
        objectList = objectList.split(',')
    else:
        objectList = []
    ocel, objectTypes, eventLog = loadOCEventLog(filePath, fileExtension, ocelVersion, objectList)
    print('Importing event log completed')
    eventLogForMiner = generateEventLogForMiner(eventLog, objectTypes)
    objectSet = set(eventLogForMiner['object'])
    eventLogDict = generateEventLogDict(eventLogForMiner)
    heuNets = mineHeuNets(eventLogForMiner.rename(columns={'event_activity':'concept:name', 'event_timestamp':'time:timestamp', 'object':'case:concept:name'}), objectTypes, dependency_threshold, and_threshold, loop_two_threshold)
    events = getEvents(heuNets)
    dependencyDict, startActivities, endActivities = generateDependencyDict(heuNets, objectTypes, events, [], 1)
    dependencyGraph = generateDependencyGraph(dependencyDict)
    print('Object-centric dependency graph completed')
    predecessorDict = dependencyGraph._pred
    successorDict = dependencyGraph._succ
    predecessors = getPredecessors(events, predecessorDict)
    successors = getSuccessors(events, successorDict)
    closestPredecessorDF = generateClosestPredecessorDF(objectSet, eventLogDict, predecessors)
    closestSuccessorDF = generateClosestSuccessorDF(objectSet, eventLogDict, successors)
    print('Mining all closest predecessors and successors completed')
    eventToActivityDict = pd.Series(eventLog['event_activity'].values,index=eventLog['event_id']).to_dict()
    eventIDSet = set(eventToActivityDict.keys())
    outputBindings, times, outputSkippedEvents = mineOutputBindings(eventIDSet, eventToActivityDict, closestPredecessorDF, events, startActivities, dependencyDict, eventLogForMiner, combo_threshold)
    print('Mining the groups of output markers completed')
    inputBindings, inputSkippedEvents = mineInputBindings(eventIDSet, eventToActivityDict, closestSuccessorDF, events, endActivities, dependencyDict, eventLogForMiner, combo_threshold)
    print('Mining the groups of input markers completed')
    outputPath = fileName + time.strftime("_%Y-%m-%d-%H-%M-%S/", time.gmtime())
    activityCount = generateActivityCount(eventLog, startActivities, endActivities)
    os.makedirs(os.path.dirname(outputPath), exist_ok=True)
    with open(outputPath + 'inputMarkers.pkl', 'wb') as f:
        pickle.dump(inputBindings, f)
    with open(outputPath + 'outputMarkers.pkl', 'wb') as f:
        pickle.dump(outputBindings, f)
    with open(outputPath + 'dependencyGraph.pkl', 'wb') as f:
        pickle.dump(dependencyGraph, f)
    with open(outputPath + 'activityCount.pkl', 'wb') as f:
        pickle.dump(activityCount, f)
    with open(outputPath + 'inputMarkersSkippedEvents.txt', 'w') as f:
        for line in inputSkippedEvents:
            f.write(f"{line}\n")
    with open(outputPath + 'outputMarkersSkippedEvents.txt', 'w') as f:
        for line in outputSkippedEvents:
            f.write(f"{line}\n")
    with open(outputPath + 'parameters.txt', 'w') as f:
        for line in [dependency_threshold, dependency_threshold, loop_two_threshold, combo_threshold]:
            f.write(f"{line}\n")
    print('Saved object-centric causal net to ' + os.path.abspath(outputPath))
    vizBool = input('Visualize OCCN? (y/n): ')
    if vizBool == 'y':
        vizFilePath = 'visualization/'#input('Absolute path to visualization folder: ').strip('"')
        while vizBool == 'y':
            relativeOccuranceThreshold = float(input('Relative frequency treshold: '))
            visualizer(dependencyGraph, outputBindings, inputBindings, activityCount, relativeOccuranceThreshold, vizFilePath)
            vizBool = input('Try another relative frequency treshold? (y/n): ')
#%%
if __name__ == '__main__':
    main()