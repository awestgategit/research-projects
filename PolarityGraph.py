"""
Adam Westgate
An implementation of the Polarity Graph algorithm. This algorithm was the subject of the conference paper "A Graph Based Approach to Sentiment Lexicon Expansion" for IEA-AIE 2018 in Montreal.

The algorithm aim to analyze the polarity of a word given a limited lexicon. It handles this by constructing a graph from its synonyms, forming a path through the graph and then obtaining a polarity based on that path.
"""


from PyDictionary import PyDictionary as PyDict
from textblob import TextBlob
import math

TARGET_WORD = "terrible" #Word being analyzed
NUM_SYNS = 6 #Synonym limit for each layer of the graph, to prevent excessive memory usage.

antonym = ""
def generate_graph(graph):
"""
Generates the graph by pulling synonyms of the target word from Thesaurus.com (using PyDict). Afterwards, synonyms of those words are grabbed and added in as a second layer of the graph.
This process is continued until the an antonym of the target word is found.

Input:
    graph - an empty dict for the graph to be stored in
Output:
    A completed graph as a dictionary of words and the synonyms they point to.
"""

    global antonym

    prev_syns = [TARGET_WORD]
    print(PyDict.antonym(TARGET_WORD))

    for syn in prev_syns:
        
        if any(i in prev_syns for i in PyDict.antonym(TARGET_WORD)):
            antonym_tempset = set(prev_syns).intersection(PyDict.antonym(TARGET_WORD))
            antonym = list(antonym_tempset)[0]
            break
        
        if not graph.get(syn) and PyDict.synonym(syn):
            graph[syn] = PyDict.synonym(syn)[:NUM_SYNS]
            prev_syns += PyDict.synonym(syn)[:NUM_SYNS]

    return graph

def find_all_paths(graph, start, end, path=[]):
"""
Finds all paths from the target word to the first antonym.

Inputs:
    graph - the graph itself stored as a dictionary
    start - the start node of the path. Will be the target word in this case.
    end - the final node of the path. Will be the antonym in this case.
    path - a possible path, passed as an argument because its recursively constructed.

Outputs:
    paths - a list of possible paths

"""
        path = path + [start]
        if start == end:
            return [path]
        if start not in graph:
            return []
        paths = []
        for node in graph[start]:
            if node not in path:
                newpaths = find_all_paths(graph, node, end, path)
                for newpath in newpaths:
                    paths.append(newpath)
        return paths

def find_optimal_paths(paths):
"""
Narrows down the list of potential paths to a list of optimal paths.
Optimal paths are paths that contain several consecutive nodes of the same sign (the amount of consecutive nodes must be greater than or equal to half the length of the path itself).
"""

    same_sign = 1
    optimals = []

    for path in paths:
        same_counter = 0
        init_sign = math.copysign(1,TextBlob(path[0]).sentiment.polarity)
        same_sign_thresh = math.floor(len(path)/2)
        for node in path:
            if same_counter >= same_sign_thresh:
                optimals.append(path)
                break
            if math.copysign(1,TextBlob(node).sentiment.polarity) == init_sign:
                same_counter += 1
            else:
                init_sign = math.copysign(1,TextBlob(node).sentiment.polarity)
                same_counter = 0

    return optimals

def find_best_optimal(optimal_paths):
"""
Sorts out the best path from the list of optimal paths.
"""

    best_optimal = []

    for optimal in optimal_paths:
        if len(optimal) >= len(best_optimal):
            best_optimal = optimal

    return best_optimal

def calc_final_polarity(optimal):
"""
Takes the best optimal path and calculates its polarity based on a weighted average.
"""

    pol_sum = 0
    weight_sum = 0

    for i in range(1, len(optimal)-1):
        print(optimal[i])
        pol_sum += (TextBlob(optimal[i]).sentiment.polarity * (1/i))
        weight_sum += (1/i)

    return (pol_sum/weight_sum)

syn_graph = dict()
generate_graph(syn_graph)
print(syn_graph)
print("ANTONYM:",antonym)
potential_paths = find_all_paths(syn_graph,TARGET_WORD,antonym)
print("POTENTIALS:",potential_paths)
optimals = find_optimal_paths(potential_paths)
print("NEAR-OPTIMALS:",optimals)
print("OPTIMAL:", find_best_optimal(optimals))
print("\nPOLARITY:", calc_final_polarity(find_best_optimal(optimals)))
