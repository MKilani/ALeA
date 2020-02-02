import json

from ASeT import ASeT

#---- you neet to modify the following five arguments:

pathModel = "/path/to/folder/model/NameModel" # (e.g. name model: generated_model_google )
pathListSemanticTags = "/path/to/folder/concepts_list/consepticon_1.0_multiLevel.txt"

pathHebrewAramaicListRaw = "/path/to/folder/with/raw/list/Hebrew-Aramaic_raw.json"

pathOutputEgyptian = "/path/to/folder/to/print/results/EgyptianWords_tagged_multilevel_2"
pathOutputHebrewAramaic = "/path/to/folder/to/print/results/Hebrew-Aramaic_tagged_multilevel_2"


#---- and you need to select what list you want to tag by uncommenting the appopriate line

tag = "Hebrew-Aramaic"
#tag = "Egyptian"

#-------------------
#-------------------

#Arguments:

EgyptianWordsToTag = [[0, "a tree", ["ʔln"]],[1, "quiver", ["ʔspt"]], [2, "assist, assisting person, aide", ["ʕʣr"]], [3, "peak, top, summit", ["rʔʃ"]], [4, "scribe", ["ʦpr"]], [5, "skillful, know", ["jdʕ"]]] #

verbose = True
numberMatchesOutput = None
splitMenings = True
dividers = [","]

numberLevels = 2

semanticThreshold_lvl1=0.1
semanticThreshold_lvl2=0.45
thresholdClusters_lvl3 = None

thresholdClusters_lvl1 = 2
thresholdClusters_lvl2 = 3
semanticThreshold_lvl3 = None

#------------------------

fileRead = open(pathHebrewAramaicListRaw, "r")
HebrewList_json = fileRead.read()

if tag == "Egyptian":

    wordsToTag = EgyptianWordsToTag
    pathOutput = pathOutputEgyptian

elif tag = "Hebrew-Aramaic":

    wordsToTag = json.loads(HebrewList_json)
    pathOutput = pathOutputHebrewAramaic

fileRead = open(pathListSemanticTags, "r")
listSemanticTags_json = fileRead.read()
listSemanticTags = json.loads(listSemanticTags_json)




resultsSimplified, resultsJson = ASeT( \
    wordsToTag,  \
    listSemanticTags, \
    pathModel, \
    pathOutput, \
    numberLevels, \
    numberMatchesOutput, \
    verbose, \
    splitMenings, \
    dividers, \
    semanticThreshold_lvl1, \
    semanticThreshold_lvl2, \
    semanticThreshold_lvl3, \
    thresholdClusters_lvl1, \
    thresholdClusters_lvl2, \
    thresholdClusters_lvl3)

print(resultsSimplified)
print(resultsJson)

