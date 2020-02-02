from ALeA import ALeA
from ALeA import initializeFAAL

import json

#---- you neet to modify the following four arguments

pathList1 = "/path/to/folder/tagged/wordlists/EgyptianWords_tagged_multilevel_2.json"

pathList2 = "/path/to/folder/tagged/wordlists/Hebrew-Aramaic_tagged_multilevel_2.json"

pathOutput = "/path/to/folder/to/print/results/NameOutput" # no extension

pathModel = "/path/to/folder/model/NameModel" # (e.g. name model: generated_model_google )



#initialize the FAAl aligning algorithm - note: the java program needs to be shut down and initialized again at every new run
initializeFAAL()

fileRead_1 = open(pathList1, "r")

fileRead_2 = open(pathList2, "r")

json_semanticSelection_One = fileRead_1.read()
json_semanticSelection_Two = fileRead_2.read()

json_semanticSelectionDict, json_semanticSelectionDict_best, results_best_Simplified = ALeA(json_semanticSelection_One, \
                                                                                            json_semanticSelection_Two, \
                                                                                            pathModel, \
                                                                                            pathOutput, \
                                                                                            scoreAlignPhon = "10_Aver_Score_Sem-Phon_Glob", \
                                                                                            verbose = True, \
                                                                                            semanticLevel = "Level_02", \
                                                                                            dividers = [","], \
                                                                                            selectBest = "09_Aver_Score_Sem-Phon_Corr", \
                                                                                            selectBestThreshold = 0.6, \
                                                                                            parseVow = False)



print (json_semanticSelectionDict)
print (json_semanticSelectionDict_best)


for item in results_best_Simplified:
    print (item)