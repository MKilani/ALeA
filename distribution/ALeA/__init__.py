from .dependencies.interfaceFAAL import interfaceFAAL
from gensim.test.utils import datapath
from gensim.models import KeyedVectors
from gensim.similarities import WmdSimilarity
import json
import os
import subprocess

from .progbar import progbar

def initializeFAAL():

    

    jarFolder = os.path.join(os.path.dirname(__file__), 'dependencies', 'FAAL_jar')

    process = subprocess.Popen('java -jar FAAL_jar_Global_ALeA.jar',
                               cwd=jarFolder,
                               stdout=subprocess.PIPE, shell=True)

    while True:
        output = process.stdout.readline()
        if not output == '':
            print("FAAL jar is running...")
            break
    return process

def terminateFAAL(process):
    process.terminate()


def ALeA(json_semanticSelection_One, json_semanticSelection_Two, pathModel, scoreAlignPhon = "09_Aver_Score_Sem-Phon_Corr", verbose = False, semanticLevel = "Level_01", dividers = [","], phoneticThreshold = 0.65):
    """
    :param json_semanticSelection: output of the semanticComparison method.
                -- format: json string
    :param scoreAlignPhon: select type of score according to which the phonetic alignments are organized (string)
            -- default: "bestAlignCorrected"
            -- options: "bestAlignCorrected" or "bestAlignGlobal"
            -- "bestAlignCorrected" uses the function "(((SumFeat) / (NrFeat * 7.71)) - ((LenSeq - ShortestWord)/1.04 + ((LenAlign - LenSeq)/LenSeq)) * (1-(ShortestWord/LongestWord))) / (LenAlign * 4.77117)"
            -- see FAAL documentation for details ( https://github.com/MKilani/FAAL )
    :param verbose: print data during execution (boolean)
            -- default: False
    :return: results (json string)
            -- format:
                {
                   "0": {                                           # ID entry - index for the following data
                      "0_ID_token": int,                            # ID item lexical list A
                      "1_Meaning_token": string,                    # Meaning(s) item lexical list A
                      "2_Form_token": [                             # Form(s) item lexical list A - spelled in IPA
                         string,
                         string
                      ],
                      "3_Matches": {                                # Organized matches from lexical list B - index for the matches
                         "0": {                                     # ID match
                            "0_ID_Match": int,                      # ID item from lexical list B
                            "1_Meaning_Match": string,              # Meaning(s) item lexical list B
                            "2_Form_Match": [                       # Form(s) item lexical list B - spelled in IPA
                               string,
                               string
                            ],
                            "3_Sim_Score_Sem_Match": float,         # Semantic similarity item list A - item list B
                            "4_Best_Match_Sem": [                   # Meanings of items list A and B with highest semantic similarity
                               string,
                               string
                            ],
                            "5_Best_Match_Phon": [                  # Forms of items list A and B with highest phonetic similarity
                               int,
                               string,
                               int,
                               string
                            ],
                            "6_Sim_Score_Phon_Corr_Match": float,   # Phonetic alignemnt - Corrected similarity score (see FAAL documentation)
                            "7_Sim_Score_Phon_Glob_Match": float,   # Phonetic alignemnt - Global similarity score (see FAAL documentation)
                            "8_Aver_Score_Sem-Phon_Corr": float,    # Phonetic-Semantic alignemnt - Average Corrected similarity score - Semantic score
                            "9_ResultsComp": {
                               "bestAlignCorrected": float,         # Phonetic alignemnt - Corrected similarity score (see FAAL documentation)
                               "bestAlignGlobal": float,            # Phonetic alignemnt - Global similarity score (see FAAL documentation)
                               "wordWithDiacritics_1": string,      # Alignment with diacritic - word A (see FAAL documentation)
                               "wordWithDiacritics_2": string,      # Alignment with diacritic - word B (see FAAL documentation)
                               "wordWithoutDiacritics_1": string,   # Alignment without diacritic - word A (see FAAL documentation)
                               "wordWithoutDiacritics_2": string    # Alignment without diacritic - word B (see FAAL documentation)
                            }
                         },
                         etc.
                      }
                   },
                   etc.
                 }
    """

    semanticSelectionDict_One = json.loads(json_semanticSelection_One)
    semanticSelectionDict_Two = json.loads(json_semanticSelection_Two)

    semanticSelectionDict = {}



    SemanticIndex_ListTwo = {}

    for key_Two in semanticSelectionDict_Two:
        entryTwo = semanticSelectionDict_Two[key_Two]
        ID_Token = entryTwo["00_ID_token"]
        for match_ID in entryTwo["03_Matches"][semanticLevel]:
            semantic_item_temp = entryTwo["03_Matches"][semanticLevel][match_ID]["11_Semantic_Field"]
            ID_Cluster = entryTwo["03_Matches"][semanticLevel][match_ID]["05_ID_Cluster"]

            if semantic_item_temp in SemanticIndex_ListTwo:
                SemanticIndex_ListTwo[semantic_item_temp].append({"Key" : key_Two, "ID_token" : ID_Token, "ID_match" : match_ID, "ID_Cluster" : ID_Cluster})
            else:
                SemanticIndex_ListTwo[semantic_item_temp] = [{"Key" : key_Two, "ID_token" : ID_Token, "ID_match" : match_ID, "ID_Cluster" : ID_Cluster}]


    hurry = SemanticIndex_ListTwo["hurry"]



    #Combine lists

    counterNewPairs = 0

    print("*- Phonetic comparison -*")
    print("-> Start")

    # set up progress bar
    indexBar = -1
    print("Progress:")

    for key_One in semanticSelectionDict_One:

        indexBar = indexBar + 1

        entry = semanticSelectionDict_One[key_One]
        ID_Token_00 = entry["00_ID_token"]
        Meaning_token_01 = entry["01_Meaning_token"]
        Form_token_02 = entry["02_Form_token"]
        last_match = list(entry["03_Matches"][semanticLevel].keys())[-1]
        max_cluster_ID = entry["03_Matches"][semanticLevel][last_match]["05_ID_Cluster"]
        for new_ID_cluster in range(0, max_cluster_ID+1):
            new_entry = {}
            new_entry["00_ID_token"] = ID_Token_00
            new_entry["01_Meaning_token"] = Meaning_token_01
            new_entry["02_Form_token"] = Form_token_02

            new_match_count = 0
            new_matches = {}
            for match_ID in entry["03_Matches"][semanticLevel]:
                if entry["03_Matches"][semanticLevel][match_ID]["05_ID_Cluster"] > new_ID_cluster:
                    continue

                if entry["03_Matches"][semanticLevel][match_ID]["05_ID_Cluster"] <= new_ID_cluster:
                    semanticToMatch = entry["03_Matches"][semanticLevel][match_ID]["11_Semantic_Field"]

                    #new_match_count = 0
                    for matchTwo in SemanticIndex_ListTwo[semanticToMatch]:

                        progbar(indexBar, len(semanticSelectionDict_One) - 1, 20)

                        new_match = {}

                        if matchTwo["ID_Cluster"] <= new_ID_cluster:
                            entry_Two = semanticSelectionDict_Two[matchTwo["Key"]]

                            new_match["00_ID_Match"] = entry_Two["00_ID_token"]
                            new_match["01_Meaning_Match"] = entry_Two["01_Meaning_token"]
                            new_match["02_Form_Match"] = entry_Two["02_Form_token"]
                            new_match["03_Best_Match_Sem"] = [semanticToMatch, semanticToMatch]
                            new_match["05_ID_Cluster"] = new_ID_cluster
                            new_match["06_Sim_Score_Sem_Match"] = 1.0
                            new_match["11_Semantic_Field"] = semanticToMatch

                            new_matches[new_match_count] = new_match.copy()
                            new_match_count = new_match_count + 1

            new_entry["03_Matches"] = {}
            new_entry["03_Matches"][semanticLevel] = new_matches

            semanticSelectionDict[counterNewPairs] = {}
            semanticSelectionDict[counterNewPairs][new_ID_cluster] = new_entry
            counterNewPairs = counterNewPairs + 1







    print ()



    print("-> Load Model")

    # load the google word2vec model
    temp_file = datapath(pathModel)
    model = KeyedVectors.load(temp_file)

    print("-> Model loaded")

    counter = 0
    for key_A in semanticSelectionDict:
        for sem_Cluster in semanticSelectionDict[key_A]:

            meaningRaw = semanticSelectionDict[key_A][sem_Cluster]['01_Meaning_token']



            for divider in dividers:

                meaningRaw = meaningRaw.replace(divider, "£")

            meaningRaw = meaningRaw.replace("  ", " ")
            meaningRaw = meaningRaw.replace("  ", " ")
            meaningRaw = meaningRaw.replace("  ", " ")
            meaningRaw = meaningRaw.replace("£ ", "£")
            meaningRaw = meaningRaw.replace(" £", "£")

            listMeaningsSplit = meaningRaw.split("£")
            listMeanings =[]
            for ID in range(0, len(listMeaningsSplit)):
                listMeanings.append(listMeaningsSplit[ID].split(" "))

            numberMatchesOutput = len(listMeanings)

            print("-> Compile semantic index")
            print (str(counter) + " of " + str(len(semanticSelectionDict)))
            counter = counter + 1
            index = WmdSimilarity(listMeanings, model, numberMatchesOutput)
            print("-> Semantic index compiled")


            for key_B in semanticSelectionDict[key_A][sem_Cluster]["03_Matches"][semanticLevel]:

                meaningToCheckRaw = semanticSelectionDict[key_A][sem_Cluster]["03_Matches"][semanticLevel][key_B]["01_Meaning_Match"]

                for divider in dividers:
                    meaningToCheckRaw = meaningToCheckRaw.replace(divider, "£")

                meaningToCheckRaw = meaningToCheckRaw.replace("  ", " ")
                meaningToCheckRaw = meaningToCheckRaw.replace("  ", " ")
                meaningToCheckRaw = meaningToCheckRaw.replace("  ", " ")
                meaningToCheckRaw = meaningToCheckRaw.replace("£ ", "£")
                meaningToCheckRaw = meaningToCheckRaw.replace(" £", "£")

                meaningToCheck = meaningToCheckRaw.split("£")

                bestResult = 0.0
                bestMatch = ["", ""]

                for meaning in meaningToCheck:
                    query = [meaning]
                    resultsQuery = index[query]
                    resultsQueryWithIndexes = list(enumerate(resultsQuery))
                    if len(resultsQueryWithIndexes) > 0:
                        if resultsQueryWithIndexes[0][1][1] > bestResult:
                            bestResult = resultsQueryWithIndexes[0][1][1]
                            bestMatch = []
                            bestMatch.append(" ".join(listMeanings[resultsQueryWithIndexes[0][1][0]]))
                            bestMatch.append(meaning)

                semanticSelectionDict[key_A][sem_Cluster]["03_Matches"][semanticLevel][key_B]["06_Sim_Score_Sem_Match"] = bestResult
                semanticSelectionDict[key_A][sem_Cluster]["03_Matches"][semanticLevel][key_B]["03_Best_Match_Sem"] = bestMatch
                #semanticSelectionDict[key_A][sem_Cluster]["03_Matches"][semanticLevel][key_B]['09_Aver_Score_Sem-Phon_Corr'] = (semanticSelectionDict[key_A][sem_Cluster]["03_Matches"][semanticLevel][key_B]["07_Sim_Score_Phon_Corr_Match"] + semanticSelectionDict[key_A][sem_Cluster]["03_Matches"][semanticLevel][key_B]["06_Sim_Score_Sem_Match"]) / 2





    print("*- Phonetic comparison -*")
    print("-> Start")

    # set up progress bar
    indexBar = -1
    print ("Progress:")

    for key_A in semanticSelectionDict:
        for sem_Cluster in semanticSelectionDict[key_A]:

            indexBar = indexBar + 1
            progbar(indexBar, len(semanticSelectionDict) - 1, 20)

            if semanticSelectionDict[key_A][sem_Cluster]["03_Matches"][semanticLevel] == {}:
                continue



            ID_word_A = semanticSelectionDict[key_A][sem_Cluster]['00_ID_token']
            meaning_word_A = semanticSelectionDict[key_A][sem_Cluster]['01_Meaning_token']
            word_A_list = semanticSelectionDict[key_A][sem_Cluster]['02_Form_token']

            #print (word_A)
            for key_B in semanticSelectionDict[key_A][sem_Cluster]["03_Matches"][semanticLevel]:
                ID_word_B = semanticSelectionDict[key_A][sem_Cluster]["03_Matches"][semanticLevel][key_B]["00_ID_Match"]
                meaning_word_B = semanticSelectionDict[key_A][sem_Cluster]["03_Matches"][semanticLevel][key_B]["01_Meaning_Match"]
                word_B_list = semanticSelectionDict[key_A][sem_Cluster]["03_Matches"][semanticLevel][key_B]["02_Form_Match"]

                resultsComparison = {}
                IDBestMatch = []

                #Compare phonetically FAAL - when more than one varian, select that providing the best alignment according to the selected score "score"
                index_WordA = -1
                for word_A in word_A_list:
                    index_WordA = index_WordA + 1
                    index_WordB = -1
                    for word_B in word_B_list:
                        index_WordB = index_WordB + 1
                        resultsComparisonTemp = interfaceFAAL(word_A, word_B)



                            #print (resultsComparisonTemp)

                        if resultsComparison == {}:
                            resultsComparison = resultsComparisonTemp
                            IDBestMatch = []
                            IDBestMatch.append(index_WordA)
                            IDBestMatch.append(word_A)
                            IDBestMatch.append(index_WordB)
                            IDBestMatch.append(word_B)
                        else:
                            if resultsComparisonTemp[scoreAlignPhon] > resultsComparison[scoreAlignPhon]:
                                resultsComparison = resultsComparisonTemp
                                IDBestMatch = []
                                IDBestMatch.append(index_WordA)
                                IDBestMatch.append(word_A)
                                IDBestMatch.append(index_WordB)
                                IDBestMatch.append(word_B)

                #phoneticSelectionFile = open("/Users/iome/Desktop/dataTLA/lemmata/phonetics.txt", "a+")
                #phoneticSelectionFile.write(key_A + "||" + key_B + "||" + resultsComparison + "||" + IDBestMatch + "\n")
                #phoneticSelectionFile.close()


                semanticSelectionDict[key_A][sem_Cluster]["03_Matches"][semanticLevel][key_B]['10_ResultsComp'] = resultsComparison
                semanticSelectionDict[key_A][sem_Cluster]["03_Matches"][semanticLevel][key_B]['04_Best_Match_Phon'] = IDBestMatch
                semanticSelectionDict[key_A][sem_Cluster]["03_Matches"][semanticLevel][key_B]['07_Sim_Score_Phon_Corr_Match'] = semanticSelectionDict[key_A][sem_Cluster]["03_Matches"][semanticLevel][key_B]["10_ResultsComp"]["bestAlignCorrected"]
                semanticSelectionDict[key_A][sem_Cluster]["03_Matches"][semanticLevel][key_B]['08_Sim_Score_Phon_Glob_Match'] = semanticSelectionDict[key_A][sem_Cluster]["03_Matches"][semanticLevel][key_B]["10_ResultsComp"]["bestAlignGlobal"]
                semanticSelectionDict[key_A][sem_Cluster]["03_Matches"][semanticLevel][key_B]['09_Aver_Score_Sem-Phon_Corr'] = (semanticSelectionDict[key_A][sem_Cluster]["03_Matches"][semanticLevel][key_B]["07_Sim_Score_Phon_Corr_Match"] + semanticSelectionDict[key_A][sem_Cluster]["03_Matches"][semanticLevel][key_B]["06_Sim_Score_Sem_Match"])/2


    print ()
    # set up progress bar
    indexBar = -1
    print("Progress:")

    semanticSelectionDict_ordered = {}

    for key_A in semanticSelectionDict:

        indexBar = indexBar + 1
        progbar(indexBar, len(semanticSelectionDict) - 1, 20)

        if key_A not in semanticSelectionDict_ordered:
            semanticSelectionDict_ordered[key_A] = {}

        temporaryEntries = []

        for sem_Cluster in semanticSelectionDict[key_A]:
            if sem_Cluster not in semanticSelectionDict_ordered[key_A]:
                semanticSelectionDict_ordered[key_A][sem_Cluster] = {}
            semanticSelectionDict_ordered[key_A][sem_Cluster]["00_ID_token"] = semanticSelectionDict[key_A][sem_Cluster]["00_ID_token"]
            semanticSelectionDict_ordered[key_A][sem_Cluster]["01_Meaning_token"] = semanticSelectionDict[key_A][sem_Cluster]["01_Meaning_token"]
            semanticSelectionDict_ordered[key_A][sem_Cluster]["02_Form_token"] = semanticSelectionDict[key_A][sem_Cluster]["02_Form_token"]

            if semanticSelectionDict[key_A][sem_Cluster]["03_Matches"][semanticLevel] == {}:
                semanticSelectionDict_ordered[key_A][sem_Cluster]["03_Matches"] = {}
                semanticSelectionDict_ordered[key_A][sem_Cluster]["03_Matches"][semanticLevel] = semanticSelectionDict[key_A][sem_Cluster]["03_Matches"][semanticLevel]
                continue

            for n in range(0, len(semanticSelectionDict[key_A][sem_Cluster]["03_Matches"][semanticLevel])):




                if len(temporaryEntries) == 0:

                    temporaryEntries.append(semanticSelectionDict[key_A][sem_Cluster]["03_Matches"][semanticLevel][0])
                else:

                    if semanticSelectionDict[key_A][sem_Cluster]["03_Matches"][semanticLevel][n][scoreAlignPhon] >= temporaryEntries[0][scoreAlignPhon]:
                        temporaryEntries.insert(0, semanticSelectionDict[key_A][sem_Cluster]["03_Matches"][semanticLevel][n])

                    elif semanticSelectionDict[key_A][sem_Cluster]["03_Matches"][semanticLevel][n][scoreAlignPhon] < \
                            temporaryEntries[-1][scoreAlignPhon]:
                        temporaryEntries.append(semanticSelectionDict[key_A][sem_Cluster]["03_Matches"][semanticLevel][n])

                    else:
                        for z in range(1, len(temporaryEntries)):
                            if semanticSelectionDict[key_A][sem_Cluster]["03_Matches"][semanticLevel][n]\
                                            [scoreAlignPhon] < temporaryEntries[z-1][scoreAlignPhon] and \
                                            semanticSelectionDict[key_A][sem_Cluster]["03_Matches"][semanticLevel][n] \
                                            [scoreAlignPhon] >= temporaryEntries[z][scoreAlignPhon]:
                                temporaryEntries.insert(z,semanticSelectionDict[key_A][sem_Cluster]["03_Matches"][semanticLevel][n])
                                break

            semanticSelectionDict_ordered[key_A][sem_Cluster]["03_Matches"] = {}
            semanticSelectionDict_ordered[key_A][sem_Cluster]["03_Matches"][semanticLevel] = {}
            for ID in range (0, len(temporaryEntries)):
                semanticSelectionDict_ordered[key_A][sem_Cluster]["03_Matches"][semanticLevel][ID] = temporaryEntries[ID]


    json_semanticSelectionDict = json.dumps(semanticSelectionDict_ordered, sort_keys=True, indent=3, ensure_ascii=False)

    #print(json_semanticSelectionDict)

    print()
    print("-> End")




    print()
    # set up progress bar
    indexBar = -1
    print("Select top matches - Progress:")

    semanticSelectionDict = json.loads(alignedLists)

    for key_A in semanticSelectionDict:

        indexBar = indexBar + 1
        progbar(indexBar, len(semanticSelectionDict) - 1, 20)

        if key_A not in semanticSelectionDict_ordered:
            semanticSelectionDict_ordered[key_A] = {}

        temporaryEntries = []

        counter = 0

        for sem_Cluster in semanticSelectionDict[key_A]:
            if sem_Cluster not in semanticSelectionDict_ordered[key_A]:
                semanticSelectionDict_ordered[key_A][sem_Cluster] = {}
            semanticSelectionDict_ordered[key_A][sem_Cluster]["00_ID_token"] = \
            semanticSelectionDict[key_A][sem_Cluster]["00_ID_token"]
            semanticSelectionDict_ordered[key_A][sem_Cluster]["01_Meaning_token"] = \
            semanticSelectionDict[key_A][sem_Cluster]["01_Meaning_token"]
            semanticSelectionDict_ordered[key_A][sem_Cluster]["02_Form_token"] = \
            semanticSelectionDict[key_A][sem_Cluster]["02_Form_token"]

            if semanticSelectionDict[key_A][sem_Cluster]["03_Matches"][semanticLevel] == {}:
                semanticSelectionDict_ordered[key_A][sem_Cluster]["03_Matches"] = {}
                semanticSelectionDict_ordered[key_A][sem_Cluster]["03_Matches"][semanticLevel] = \
                semanticSelectionDict[key_A][sem_Cluster]["03_Matches"][semanticLevel]
                continue

            for n in range(0, len(semanticSelectionDict[key_A][sem_Cluster]["03_Matches"][semanticLevel])):

                if len(temporaryEntries) == 0:

                    temporaryEntries.append(
                        semanticSelectionDict[key_A][sem_Cluster]["03_Matches"][semanticLevel][str(0)])
                else:

                    if semanticSelectionDict[key_A][sem_Cluster]["03_Matches"][semanticLevel][str(n)][
                        scoreAlignPhon] > phoneticThreshold:
                        temporaryEntries.append(
                            semanticSelectionDict[key_A][sem_Cluster]["03_Matches"][semanticLevel][str(n)])

        semanticSelectionDict_ordered[key_A][sem_Cluster]["03_Matches"] = {}
        semanticSelectionDict_ordered[key_A][sem_Cluster]["03_Matches"][semanticLevel] = {}
        for ID in range(0, len(temporaryEntries)):
            semanticSelectionDict_ordered[key_A][sem_Cluster]["03_Matches"][semanticLevel][str(ID)] = temporaryEntries[
                ID]


    json_semanticSelectionDict_best = json.dumps(semanticSelectionDict_ordered, sort_keys=True, indent=3,\
                                                 ensure_ascii=False)







    return json_semanticSelectionDict, json_semanticSelectionDict_best