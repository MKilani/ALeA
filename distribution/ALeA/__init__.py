from .dependencies.interfaceFAAL import interfaceFAAL
from gensim.test.utils import datapath
from gensim.models import KeyedVectors
from gensim.similarities import WmdSimilarity
import json
import os
from subprocess import *
import copy
from py4j.java_gateway import JavaGateway, GatewayParameters

from .progbar import progbar

def initializeFAAL():

    jarFAAL = os.path.join(os.path.dirname(__file__), 'dependencies', 'FAAL_jar', 'FAAL_jar_Global_ALeA.jar')
    jarFolder = os.path.join(os.path.dirname(__file__), 'dependencies', 'FAAL_jar')

    #process = call(['java', '-jar', jarFAAL], stdout=PIPE, #stderr=PIPE,
    #                           cwd=jarFolder)
    process = Popen(['java', '-jar', jarFAAL], #stdout=PIPE, #stderr=PIPE,
                               cwd=jarFolder)

    #process = os.system("java -jar " + jarFAAL)

    #while True:
    #    output = process.stdout.readline()
    #    if not output == '':
    #        print("FAAL jar is running...")
    #        break
    return process

def terminateFAAL(process):
    process.terminate()


def ALeA(json_semanticSelection_One, json_semanticSelection_Two, pathModel, pathOutput, scoreAlignPhon = "09_Aver_Score_Sem-Phon_Corr", verbose = False, semanticLevel = "Level_01", dividers = [","], selectBest = "07_Sim_Score_Phon_Corr_Match", selectBestThreshold = 0.65, parseVow = True):
    """
    :param json_semanticSelection_One: first semantically tagged lexical list
                -- format: json string - output of the ASeT algorithm
    :param json_semanticSelection_Two: second semantically tagged lexical list
                -- format: json string - output of the ASeT algorithm
    :param pathModel: path to saved semantic model (string)
    :param pathOutput: path to save the results (string - no extention; e.g. /my/folder/name_file_with_my_results)
    :param scoreAlignPhon: select type of score according to which the phonetic alignments are organized (string)
            -- default: "09_Aver_Score_Sem-Phon_Corr"
            -- options: "07_Sim_Score_Phon_Corr_Match", "08_Sim_Score_Phon_Glob_Match", "09_Aver_Score_Sem-Phon_Corr", or "10_Aver_Score_Sem-Phon_Glob"
            -- "07_Sim_Score_Phon_Corr_Match" uses the function "(((SumFeat) / (NrFeat * 7.71)) / (LenAlign * 4.77117)"
            -- "09_Aver_Score_Sem-Phon_Corr" is the average between the semantic score and the "07_Sim_Score_Phon_Corr_Match"
            -- "10_Aver_Score_Sem-Phon_Glob" is the average between the semantic score and the "08_Sim_Score_Phon_Glob_Match"
            -- see FAAL documentation for details ( https://github.com/MKilani/FAAL )
    :param verbose: print data during execution (boolean)
            -- default: True
    :param semanticLevel: level of the semantic tags according to which the comaprison is performed. The options, for now, are: "Level_01", "Level_02", "Level_03" (see ASeT algorithm for details)
    :param dividers: dividers used to split meanings (array of strings [string, string]
            -- default: [","]
    :param selectBest: parameter according to which the algorithm selects the best matches among those identified by the ALeA on the basis of the other parameters
            -- default: "07_Sim_Score_Phon_Corr_Match"
            -- options: "07_Sim_Score_Phon_Corr_Match", "08_Sim_Score_Phon_Glob_Match", "09_Aver_Score_Sem-Phon_Corr", or "10_Aver_Score_Sem-Phon_Glob"
            -- "07_Sim_Score_Phon_Corr_Match" uses the function "(((SumFeat) / (NrFeat * 7.71)) / (LenAlign * 4.77117)"
            -- "09_Aver_Score_Sem-Phon_Corr" is the average between the semantic score and the "07_Sim_Score_Phon_Corr_Match"
            -- "10_Aver_Score_Sem-Phon_Glob" is the average between the semantic score and the "08_Sim_Score_Phon_Glob_Match"
            -- see FAAL documentation for details ( https://github.com/MKilani/FAAL )
    :param selectBestThreshold: threshold for the parameter selectBest
            -- default: 0.65
    :param parseVow: this allows to decide if the phonetic comparison should take into consideration vowels or not. Ignoring vowels can be useful when dealing with unrelated or relatively distant languages, or with languages in which vowels are rather unstable and semantically secondary (e.g. Semitic languages)
            -- default: True
    """
    gateway = JavaGateway()
    addition_app = gateway.entry_point

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
                    if semanticToMatch in SemanticIndex_ListTwo:
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
            print (str(counter+1) + " of " + str(len(semanticSelectionDict)))
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
            previous_Key = ""
            for key_B in semanticSelectionDict[key_A][sem_Cluster]["03_Matches"][semanticLevel]:

                if key_B == previous_Key:
                    continue
                previous_Key = key_B



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

                        if parseVow == False:
                            noVowWord_A = removeVow(word_A)
                            noVowWord_B = removeVow(word_B)

                            resultsComparisonTemp = interfaceFAAL(noVowWord_A, noVowWord_B, addition_app)

                        else:
                            resultsComparisonTemp = interfaceFAAL(word_A, word_B)

                        #indexBar = indexBar + 1
                        #progbar(indexBar, (len(semanticSelectionDict)*len(semanticSelectionDict[key_A])* len(semanticSelectionDict[key_A][sem_Cluster]["03_Matches"][semanticLevel])*len(word_A_list)* len(word_B_list)) - 1, 20)


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


                semanticSelectionDict[key_A][sem_Cluster]["03_Matches"][semanticLevel][key_B]['12_ResultsComp'] = resultsComparison
                semanticSelectionDict[key_A][sem_Cluster]["03_Matches"][semanticLevel][key_B]['04_Best_Match_Phon'] = IDBestMatch
                semanticSelectionDict[key_A][sem_Cluster]["03_Matches"][semanticLevel][key_B]['07_Sim_Score_Phon_Corr_Match'] = semanticSelectionDict[key_A][sem_Cluster]["03_Matches"][semanticLevel][key_B]["12_ResultsComp"]["bestAlignCorrected"]
                semanticSelectionDict[key_A][sem_Cluster]["03_Matches"][semanticLevel][key_B]['08_Sim_Score_Phon_Glob_Match'] = semanticSelectionDict[key_A][sem_Cluster]["03_Matches"][semanticLevel][key_B]["12_ResultsComp"]["bestAlignGlobal"]
                semanticSelectionDict[key_A][sem_Cluster]["03_Matches"][semanticLevel][key_B]['09_Aver_Score_Sem-Phon_Corr'] = (semanticSelectionDict[key_A][sem_Cluster]["03_Matches"][semanticLevel][key_B]["07_Sim_Score_Phon_Corr_Match"] + semanticSelectionDict[key_A][sem_Cluster]["03_Matches"][semanticLevel][key_B]["06_Sim_Score_Sem_Match"])/2
                semanticSelectionDict[key_A][sem_Cluster]["03_Matches"][semanticLevel][key_B]['10_Aver_Score_Sem-Phon_Glob'] = (semanticSelectionDict[key_A][sem_Cluster]["03_Matches"][semanticLevel][key_B]["08_Sim_Score_Phon_Glob_Match"] + semanticSelectionDict[key_A][sem_Cluster]["03_Matches"][semanticLevel][key_B]["06_Sim_Score_Sem_Match"]) / 2

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
                                #if not semanticSelectionDict[key_A][sem_Cluster]["03_Matches"][semanticLevel][n]\
                                #            [scoreAlignPhon] < temporaryEntries[z-1][scoreAlignPhon] and \
                                #            semanticSelectionDict[key_A][sem_Cluster]["03_Matches"][semanticLevel][n] \
                                #            ["00_ID_Match"] == temporaryEntries[z]["00_ID_Match"]:
                                temporaryEntries.insert(z,semanticSelectionDict[key_A][sem_Cluster]["03_Matches"][semanticLevel][n])
                                break

            semanticSelectionDict_ordered[key_A][sem_Cluster]["03_Matches"] = {}
            semanticSelectionDict_ordered[key_A][sem_Cluster]["03_Matches"][semanticLevel] = {}

            temporaryEntriesCleaned = []
            #remove doubles from temporary entry
            doubleEntry = False
            for temporaryEntry in temporaryEntries:
                for temporaryEntryCleaned in temporaryEntriesCleaned:
                    if temporaryEntry["00_ID_Match"] == temporaryEntryCleaned["00_ID_Match"]:
                        doubleEntry = True

                if doubleEntry == False:
                    temporaryEntriesCleaned.append(copy.deepcopy(temporaryEntry))
                doubleEntry = False




            for ID in range (0, len(temporaryEntriesCleaned)):
                semanticSelectionDict_ordered[key_A][sem_Cluster]["03_Matches"][semanticLevel][ID] = temporaryEntriesCleaned[ID]


    json_semanticSelectionDict = json.dumps(semanticSelectionDict_ordered, sort_keys=True, indent=3, ensure_ascii=False)

    #print(json_semanticSelectionDict)

    print()
    print("-> End")




    print()
    # set up progress bar
    indexBar = -1
    print("Select top matches - Progress:")

    semanticSelectionDict = json.loads(json_semanticSelectionDict)

    semanticSelectionDict_ordered_best = {}

    resultsSimplified = []
    resultsSimplifiedString = ""

    for key_A in semanticSelectionDict:

        indexBar = indexBar + 1
        progbar(indexBar, len(semanticSelectionDict) - 1, 20)

        if key_A not in semanticSelectionDict_ordered_best:
            semanticSelectionDict_ordered_best[key_A] = {}

        temporaryEntries = []

        counter = 0

        for sem_Cluster in semanticSelectionDict[key_A]:
            if sem_Cluster not in semanticSelectionDict_ordered_best[key_A]:
                semanticSelectionDict_ordered_best[key_A][sem_Cluster] = {}
            semanticSelectionDict_ordered_best[key_A][sem_Cluster]["00_ID_token"] = \
            semanticSelectionDict[key_A][sem_Cluster]["00_ID_token"]
            semanticSelectionDict_ordered_best[key_A][sem_Cluster]["01_Meaning_token"] = \
            semanticSelectionDict[key_A][sem_Cluster]["01_Meaning_token"]
            semanticSelectionDict_ordered_best[key_A][sem_Cluster]["02_Form_token"] = \
            semanticSelectionDict[key_A][sem_Cluster]["02_Form_token"]

            if semanticSelectionDict[key_A][sem_Cluster]["03_Matches"][semanticLevel] == {}:
                semanticSelectionDict_ordered_best[key_A][sem_Cluster]["03_Matches"] = {}
                semanticSelectionDict_ordered_best[key_A][sem_Cluster]["03_Matches"][semanticLevel] = \
                semanticSelectionDict[key_A][sem_Cluster]["03_Matches"][semanticLevel]
                continue

            for n in range(0, len(semanticSelectionDict[key_A][sem_Cluster]["03_Matches"][semanticLevel])):

                if len(temporaryEntries) == 0:

                    temporaryEntries.append(
                        semanticSelectionDict[key_A][sem_Cluster]["03_Matches"][semanticLevel][str(0)])
                else:

                    if semanticSelectionDict[key_A][sem_Cluster]["03_Matches"][semanticLevel][str(n)][
                        selectBest] > selectBestThreshold:
                        temporaryEntries.append(
                            semanticSelectionDict[key_A][sem_Cluster]["03_Matches"][semanticLevel][str(n)])

        semanticSelectionDict_ordered_best[key_A][sem_Cluster]["03_Matches"] = {}
        semanticSelectionDict_ordered_best[key_A][sem_Cluster]["03_Matches"][semanticLevel] = {}
        for ID in range(0, len(temporaryEntries)):
            semanticSelectionDict_ordered_best[key_A][sem_Cluster]["03_Matches"][semanticLevel][str(ID)] = copy.deepcopy(temporaryEntries[ID])


            resultsSimplifiedString = resultsSimplifiedString + "Cluster: " + str(sem_Cluster) + " :: " + str(semanticSelectionDict_ordered_best[key_A][sem_Cluster]["00_ID_token"]) + " - '" + ", ".join(semanticSelectionDict[key_A][sem_Cluster]["02_Form_token"]) + "' - " + \
                  semanticSelectionDict[key_A][sem_Cluster]["01_Meaning_token"] + " :: " + str(semanticSelectionDict_ordered_best[key_A][sem_Cluster]["03_Matches"][semanticLevel][str(ID)]["00_ID_Match"]) + " - '" + ", ".join(semanticSelectionDict_ordered_best[key_A][sem_Cluster]["03_Matches"][semanticLevel][str(ID)]["02_Form_Match"]) + "' - " + \
                  semanticSelectionDict_ordered_best[key_A][sem_Cluster]["03_Matches"][semanticLevel][str(ID)]["01_Meaning_Match"] + " :: " + str(semanticSelectionDict_ordered_best[key_A][sem_Cluster]["03_Matches"][semanticLevel][str(ID)][selectBest]) + "\n"
        resultsSimplifiedString = resultsSimplifiedString + "---------\n"


    if verbose == True:
        print()
        print()
        print(resultsSimplifiedString)

    json_semanticSelectionDict_best = json.dumps(semanticSelectionDict_ordered_best, sort_keys=True, indent=3, ensure_ascii=False)

    Results = open(
        pathOutput + ".json",
        "w")  # 

    Results.write(json_semanticSelectionDict)
    Results.close()

    ResultsBest = open(
        pathOutput + "_best_" + str(selectBestThreshold) + ".json",
        "w")  # 


    ResultsBest.write(json_semanticSelectionDict_best)
    ResultsBest.close()

    ResultsBestSimplified = open(
        pathOutput + "_bestSimplified_" + str(selectBestThreshold) + ".txt",
        "w")  #

    ResultsBestSimplified.write(resultsSimplifiedString)
    ResultsBestSimplified.close()

    return json_semanticSelectionDict, json_semanticSelectionDict_best, resultsSimplifiedString



def removeVow(wordToParse):

    wordToParse = "$" + wordToParse + "$"

    wordToParse = wordToParse.replace("̯", "")

    wordToParse = wordToParse.replace("͜", "")

    wordToParse = wordToParse.replace("i:", "i")
    wordToParse = wordToParse.replace("y:", "y")
    wordToParse = wordToParse.replace("ɨ:", "ɨ")
    wordToParse = wordToParse.replace("ʉ:", "ʉ")
    wordToParse = wordToParse.replace("ɯ:", "ɯ")
    wordToParse = wordToParse.replace("u:", "u")
    wordToParse = wordToParse.replace("ɪ:", "ɪ")
    wordToParse = wordToParse.replace("ʏ:", "ʏ")
    wordToParse = wordToParse.replace("ʊ:", "ʊ")
    wordToParse = wordToParse.replace("e:", "e")
    wordToParse = wordToParse.replace("ø:", "ø")
    wordToParse = wordToParse.replace("ɘ:", "ɘ")
    wordToParse = wordToParse.replace("ɵ:", "ɵ")
    wordToParse = wordToParse.replace("ɤ:", "ɤ")
    wordToParse = wordToParse.replace("o:", "o")
    wordToParse = wordToParse.replace("ɛ:", "ɛ")
    wordToParse = wordToParse.replace("œ:", "œ")
    wordToParse = wordToParse.replace("ə:", "ə")
    wordToParse = wordToParse.replace("ɞ:", "ɞ")
    wordToParse = wordToParse.replace("ʌ:", "ʌ")
    wordToParse = wordToParse.replace("ɔ:", "ɔ")
    wordToParse = wordToParse.replace("æ:", "æ")
    wordToParse = wordToParse.replace("ɶ:", "ɶ")
    wordToParse = wordToParse.replace("a:", "a")
    wordToParse = wordToParse.replace("ɑ:", "ɑ")
    wordToParse = wordToParse.replace("ɒ:", "ɒ")
    wordToParse = wordToParse.replace("ɐ:", "ɐ")
    wordToParse = wordToParse.replace("ɜ:", "ɜ")

    wordToParse = wordToParse.replace("$i", "ʔ")
    wordToParse = wordToParse.replace("$y", "ʔ")
    wordToParse = wordToParse.replace("$ɨ", "ʔ")
    wordToParse = wordToParse.replace("$ʉ", "ʔ")
    wordToParse = wordToParse.replace("$ɯ", "ʔ")
    wordToParse = wordToParse.replace("$u", "ʔ")
    wordToParse = wordToParse.replace("$ɪ", "ʔ")
    wordToParse = wordToParse.replace("$ʏ", "ʔ")
    wordToParse = wordToParse.replace("$ʊ", "ʔ")
    wordToParse = wordToParse.replace("$e", "ʔ")
    wordToParse = wordToParse.replace("$ø", "ʔ")
    wordToParse = wordToParse.replace("$ɘ", "ʔ")
    wordToParse = wordToParse.replace("$ɵ", "ʔ")
    wordToParse = wordToParse.replace("$ɤ", "ʔ")
    wordToParse = wordToParse.replace("$o", "ʔ")
    wordToParse = wordToParse.replace("$ɛ", "ʔ")
    wordToParse = wordToParse.replace("$œ", "ʔ")
    wordToParse = wordToParse.replace("$ə", "ʔ")
    wordToParse = wordToParse.replace("$ɞ", "ʔ")
    wordToParse = wordToParse.replace("$ʌ", "ʔ")
    wordToParse = wordToParse.replace("$ɔ", "ʔ")
    wordToParse = wordToParse.replace("$æ", "ʔ")
    wordToParse = wordToParse.replace("$ɶ", "ʔ")
    wordToParse = wordToParse.replace("$a", "ʔ")
    wordToParse = wordToParse.replace("$ɑ", "ʔ")
    wordToParse = wordToParse.replace("$ɒ", "ʔ")
    wordToParse = wordToParse.replace("$ɐ", "ʔ")
    wordToParse = wordToParse.replace("$ɜ", "ʔ")

    wordToParse = wordToParse.replace("i$", "ʔ")
    wordToParse = wordToParse.replace("y$", "ʔ")
    wordToParse = wordToParse.replace("ɨ$", "ʔ")
    wordToParse = wordToParse.replace("ʉ$", "ʔ")
    wordToParse = wordToParse.replace("ɯ$", "ʔ")
    wordToParse = wordToParse.replace("u$", "ʔ")
    wordToParse = wordToParse.replace("ɪ$", "ʔ")
    wordToParse = wordToParse.replace("ʏ$", "ʔ")
    wordToParse = wordToParse.replace("ʊ$", "ʔ")
    wordToParse = wordToParse.replace("e$", "ʔ")
    wordToParse = wordToParse.replace("ø$", "ʔ")
    wordToParse = wordToParse.replace("ɘ$", "ʔ")
    wordToParse = wordToParse.replace("ɵ$", "ʔ")
    wordToParse = wordToParse.replace("ɤ$", "ʔ")
    wordToParse = wordToParse.replace("o$", "ʔ")
    wordToParse = wordToParse.replace("ɛ$", "ʔ")
    wordToParse = wordToParse.replace("œ$", "ʔ")
    wordToParse = wordToParse.replace("ə$", "ʔ")
    wordToParse = wordToParse.replace("ɞ$", "ʔ")
    wordToParse = wordToParse.replace("ʌ$", "ʔ")
    wordToParse = wordToParse.replace("ɔ$", "ʔ")
    wordToParse = wordToParse.replace("æ$", "ʔ")
    wordToParse = wordToParse.replace("ɶ$", "ʔ")
    wordToParse = wordToParse.replace("a$", "ʔ")
    wordToParse = wordToParse.replace("ɑ$", "ʔ")
    wordToParse = wordToParse.replace("ɒ$", "ʔ")
    wordToParse = wordToParse.replace("ɐ$", "ʔ")
    wordToParse = wordToParse.replace("ɜ$", "ʔ")

    wordToParse = wordToParse.replace("$", "")

    wordToParse = wordToParse.replace("i", "")
    wordToParse = wordToParse.replace("y", "")
    wordToParse = wordToParse.replace("ɨ", "")
    wordToParse = wordToParse.replace("ʉ", "")
    wordToParse = wordToParse.replace("ɯ", "")
    wordToParse = wordToParse.replace("u", "")
    wordToParse = wordToParse.replace("ɪ", "")
    wordToParse = wordToParse.replace("ʏ", "")
    wordToParse = wordToParse.replace("ʊ", "")
    wordToParse = wordToParse.replace("e", "")
    wordToParse = wordToParse.replace("ø", "")
    wordToParse = wordToParse.replace("ɘ", "")
    wordToParse = wordToParse.replace("ɵ", "")
    wordToParse = wordToParse.replace("ɤ", "")
    wordToParse = wordToParse.replace("o", "")
    wordToParse = wordToParse.replace("ɛ", "")
    wordToParse = wordToParse.replace("œ", "")
    wordToParse = wordToParse.replace("ə", "")
    wordToParse = wordToParse.replace("ɞ", "")
    wordToParse = wordToParse.replace("ʌ", "")
    wordToParse = wordToParse.replace("ɔ", "")
    wordToParse = wordToParse.replace("æ", "")
    wordToParse = wordToParse.replace("ɶ", "")
    wordToParse = wordToParse.replace("a", "")
    wordToParse = wordToParse.replace("ɑ", "")
    wordToParse = wordToParse.replace("ɒ", "")
    wordToParse = wordToParse.replace("ɐ", "")
    wordToParse = wordToParse.replace("ɜ", "")

    return wordToParse