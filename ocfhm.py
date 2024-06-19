# -*- coding: utf-8 -*-
"""
Created on Sun Apr 28 15:06:46 2024

@author: Caspar Mensing
"""
from ocpa.objects.log.importer.ocel import factory as ocel1_import_factory
from ocpa.objects.log.importer.ocel2.sqlite import factory as ocel2_sqlite_import_factory
from ocpa.objects.log.importer.ocel2.xml import factory as ocel2_xml_import_factory
import pandas as pd
import pm4py
import networkx as nx
import numpy as np
import copy
import itertools
from networkx.algorithms.components.connected import connected_components
from collections import Counter
import pickle
import time
import csv
import scipy

#%%

def loadOCEventLog(filePath, fileName, fileExtension, ocelVersion, objectList = []):
    if ocelVersion == 1:
        if fileExtension == '.jsonocel':
            ocel = ocel1_import_factory.apply(filePath + fileName + fileExtension)
        else:
            raise ValueError('Unknown file extension for this OCEL version.')
    elif ocelVersion == 2:
        if fileExtension == '.xml':
            ocel = ocel2_xml_import_factory.apply(filePath + fileName + fileExtension)
        elif fileExtension == '.sqlite':
            ocel = ocel2_sqlite_import_factory.apply(filePath + fileName + fileExtension)
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

def mineOutputBindings(eventIDSet, eventToActivityDict, closestPredecessorDF, events, startActivities, dependencyDict, eventLogForMiner):
    outputBindingList = []
    skippedEvents = []
    eventCounter = 0
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
                if totalCombinations > 1000:
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

def mineInputBindings(eventIDSet, eventToActivityDict, closestSuccessorDF, events, endActivities, dependencyDict, eventLogForMiner):
    inputBindingList = []
    skippedEvents = []
    closestSuccessorDict = {k: v for k, v in closestSuccessorDF.groupby('successor_event_id')}
    defaultClosestSuccessorDict = pd.DataFrame(data=None, columns=closestSuccessorDF.columns)
    eventLogForMinerDict = {k: v for k, v in eventLogForMiner.groupby('event_id')}
    defaultEventLogForMinerDict = pd.DataFrame(data=None, columns=eventLogForMiner.columns)
    for event in eventIDSet:
        print('event ' + str(event))
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
                if totalCombinations > 1000:
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
#%%
filePath = 'datasets/event_logs/'
fileName = 'ContainerLogistics'
fileExtension = '.sqlite'
ocelVersion = 2
dependency_threshold = 0.9
and_threshold = 0.65
loop_two_threshold = 0.9
min_act_count = 1
min_dfg_occurrences = 1
inconsumableObjects = []
inconsumableThreshold = 1
objectList = ['Customer Order', 'Transport Document', 'Container', 'Handling Unit']#['applicants', 'applications', 'offers', 'vacancies']
#%%
timeTable = {}
timeTable['startTime'] = time.time()
ocel, objectTypes, eventLog = loadOCEventLog(filePath, fileName, fileExtension, ocelVersion, objectList)
print('loadEventLog completed')
timeTable['loadEventLogTime'] = time.time()
eventLogForMiner = generateEventLogForMiner(eventLog, objectTypes)
print('eventLogForMiner completed')
timeTable['eventLogForMinerTime'] = time.time()
objectSet = set(eventLogForMiner['object'])
print('objectSet completed')
timeTable['objectSetTime'] = time.time()
eventLogDict = generateEventLogDict(eventLogForMiner)
print('eventLogDict completed')
timeTable['eventLogDict'] = time.time()
heuNets = mineHeuNets(eventLogForMiner.rename(columns={'event_activity':'concept:name', 'event_timestamp':'time:timestamp', 'object':'case:concept:name'}), objectTypes, dependency_threshold, and_threshold, loop_two_threshold)
print('heuNets completed')
timeTable['heuNetsTime'] = time.time()
events = getEvents(heuNets)
print('events completed')
timeTable['eventsTime'] = time.time()
#%%
dependencyDict, startActivities, endActivities = generateDependencyDict(heuNets, objectTypes, events, inconsumableObjects, inconsumableThreshold)
print('dependencyDict completed')
timeTable['dependencyDictTime'] = time.time()
#%%
dependencyGraph = generateDependencyGraph(dependencyDict)
print('dependencyGraph completed')
timeTable['dependencyGraphTime'] = time.time()
#%%
predecessorDict = dependencyGraph._pred
print('predecessorDict completed')
timeTable['predecessorDictTime'] = time.time()
successorDict = dependencyGraph._succ
print('successorDict completed')
timeTable['successorDictTime'] = time.time()
predecessors = getPredecessors(events, predecessorDict)
print('predecessors completed')
timeTable['predecessorsTime'] = time.time()
successors = getSuccessors(events, successorDict)
print('successors completed')
timeTable['successorsTime'] = time.time()
#%%
closestPredecessorDF = generateClosestPredecessorDF(objectSet, eventLogDict, predecessors)
print('closestPredecessorDF completed')
timeTable['closestPredecessorDFTime'] = time.time()
closestSuccessorDF = generateClosestSuccessorDF(objectSet, eventLogDict, successors)
print('closestSuccessorDF completed')
timeTable['closestSuccessorDFTime'] = time.time()
#%%
eventToActivityDict = pd.Series(eventLog['event_activity'].values,index=eventLog['event_id']).to_dict()
print('eventToActivityDict completed')
timeTable['eventToActivityDictTime'] = time.time()
eventIDSet = set(eventToActivityDict.keys())
print('eventIDSet completed')
timeTable['eventIDSetTime'] = time.time()
outputBindings, times, outputSkippedEvents = mineOutputBindings(eventIDSet, eventToActivityDict, closestPredecessorDF, events, startActivities, dependencyDict, eventLogForMiner)
print('outputBindings completed')
timeTable['outputBindingsTime'] = time.time()
inputBindings, inputSkippedEvents = mineInputBindings(eventIDSet, eventToActivityDict, closestSuccessorDF, events, endActivities, dependencyDict, eventLogForMiner)
print('inputBindings completed')
timeTable['inputBindingsTime'] = time.time()
activityCount = generateActivityCount(eventLog, startActivities, endActivities)
print('activityCount completed')
timeTable['activityCountTime'] = time.time()
timeTable['endTime'] = time.time()
#%%

with open(fileName + '_' + '_'.join(map(str, objectList)) + '_unconsumable_inputBindings.pkl', 'wb') as f:
    pickle.dump(inputBindings, f)
with open(fileName + '_' + '_'.join(map(str, objectList)) + '_unconsumable_outputBindings.pkl', 'wb') as f:
    pickle.dump(outputBindings, f)
with open(fileName + '_' + '_'.join(map(str, objectList)) + '_unconsumable_activityCount.pkl', 'wb') as f:
    pickle.dump(activityCount, f)
#nx.write_gexf(dependencyGraph, fileName + '_' + '_'.join(map(str, objectList)) + '_unconsumable_dependencyGraph.xml')
with open(fileName + '_' + '_'.join(map(str, objectList)) + '_unconsumable_dependencyGraph.pkl', 'wb') as f:
    pickle.dump(dependencyGraph, f)

with open(fileName +'_'+ str(dependency_threshold) +'_'+ str(and_threshold) +'_'+ str(loop_two_threshold) + '_' + '_'.join(map(str, objectList)) + '_unconsumable_timeTable.csv', 'w') as f:
    w = csv.DictWriter(f, timeTable.keys())
    w.writeheader()
    w.writerow(timeTable)

with open(fileName + '_' + '_'.join(map(str, objectList)) + '_unconsumable_inputBindingsSkippedEvents.txt', 'w') as f:
    for line in inputSkippedEvents:
        f.write(f"{line}\n")
with open(fileName + '_' + '_'.join(map(str, objectList)) + '_unconsumable_outputBindingsSkippedEvents.txt', 'w') as f:
    for line in outputSkippedEvents:
        f.write(f"{line}\n")