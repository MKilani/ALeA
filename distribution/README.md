# ALeA : Automatic Lexical Aligner 

Version: 0.0.5b

Status: Beta

Release date: 08.01.2020

#### Authors

* **Marwan Kilani** - Swiss National Science Foundation (Mobility Grant) - Freie Universität Berlin (2019-2020)

#### How to cite

Kilani Marwan, 2020, ALeA 0.0.5b : Automatic Lexical Aligner, https://github.com/MKilani/ALeA

## Introduction

Note: for a detailed explanation of the functioning of ASeT, see Kilani forthcoming. What follows here is just a short summary of the functioning of the algorithm.

ALeA is a python library that, given two lists of words List_A and List_B, automatically identify the semantically and phonemically most similar words in List_B for each word in List_A. ALeA can be used for multiple purposes. For instance, it can be used to align lexical lists (e.g. different dictionaries for a same language), to identify related words within a given lexical list (by comparing the list with itself), to identify cognates in lexical lists of different but related languages, or between different stages of the same language, or to identify loanwords and shared wanderwords in lexical lists of unrelated languages.

The algorithm can be used with any language, as long as translations in a same single "bridge" language (e.g. English) is provided for each word in each list. The semantic analysis will be performed through this "bridge language".

The algorithm proceeds in two steps, first aligning the words semantically, and then aligning phonetically each word that has been identified as semantically compatible. More in particular:

* First, each word in each list is analysed semantically, and is labelled with a series of semantic tags describing their semantic fields. This process of semantic tagging is performed fully automatically, using the ASeT algorithm. For details, see the ASeT GitHub repository here: https://github.com/MKilani/ASeT

* Second, the algorithm semantically matches each word of List_A with each word of List_B, by looking in List_B for any word that share the same semantic tags of the target word in List_A. In this way, each word of List_A is matched with a selection of semantically compatible words from List_B. After that, the algorithm compares the phonological form of each word of List_A with the form of each semantically compatible word from List_B, looking for the phonologically more similar pair. This phonological comparison is also performed automatically, using the aligning algorithm FAAL. For details, see the FAAL GitHub repository here: https://github.com/MKilani/FAAL and [Kilani 2020]().

The result of this process is a is a combined list, in which each word of List_A is associated with selection of semantically compatible words from List_B, organized according to their phonological similarity.

It has to be stressed that obviously, the best results are obtained when this method is used as a semi-automatic approach, where the results of the automatic matching process are manually verified to eliminate possible spurious tags.

## Getting Started

### Prerequisites

You need Python 3.

### Installing

The python package can be installed through pip:

```shell
python3 -m pip install --index-url https://test.pypi.org/simple/ ALeA
```

Two commands need to be called. First, one needs to initialize the FAAL aligning algorithm using the command **initializeFAAL()** (for FAAL, see [Kilani 2020](references/bibliography.md) and my GitHub repository at [FAAL](https://github.com/MKilani/FAAL)). Then ALeA can be called.  
Then ALeA is called through the method ALeA() . See **Running the test** below.

## Input

The algorithm requires the following items:

#### Lexical List A and Lexical List B

The lexical lists provide the words that need to be compared and aligned.

The format is a list of lists, in which each item has the following form:

```
[ID_Word(int), translation(string), [form_1(string), form_2(string), etc]]
```

The translation entry must be a single string. If more translations are possible, they must be separated by a comma ','. Other separators can be declared explicitly (see below). Connecting words ("and", "of", "to", etc.), articles ("the", "a", "an") and other semantically empty terms should be avoided to avoid introducing "noise" that may reduce the performances of the algorithm.

The forms, instead, are individual entries in a list of strings. They must be transcribed un IPA in Unicode to be correctly processed by FAAL (see https://github.com/MKilani/FAAL and [Kilani 2020]() for details)

The following is a valid example (using a small set of Italian words, with IPA transcriptions for the form entries):

```
[
   [0, 'mouse', ['tɔpo']],
   [1, 'garlic', ['aʎʎo']],
   [2, 'obey, abide, carry out', ['ubbidire', 'obbedire'],
   [3, 'bread', ['pane']]
]
```


#### Semantic Model and List of Semantic Concepts

ALeA requires also a ["KeyedVectors"](https://radimrehurek.com/gensim/models/keyedvectors.html) model and a list of semantic concepts which will be used by the ASeT algorithm to perform the semantic analysis (for details on the ASeT algorithm, see https://github.com/MKilani/ASeT ).

##### Semantic Model

The word2vec pre-trained model GoogleNews-vectors-negative300 can be used - it can be download from this GitHub repository: https://github.com/mmihaltz/word2vec-GoogleNews-vectors

##### List of semantic concepts

The list must be formatted as a list of lists, in which each entry has the following format:

```
[ID_Concept(int), concept(string), ID_superodinate_concept-Level_1(int), ID_superodinate_concept-Level_2(int)]
```

Concepts can be either single words (e.g. 'body'), or small groups of related words, in which case each word most be separated by a space (e.g. 'motion movement vehicle cart').

Concepts belonging to the first semantic level must have ID_superodinate_concept-Level_1 = -1 and ID_superodinate_concept-Level_2 = -1.

Concepts belonging to the second semantic level must have ID_superodinate_concept-Level_2 = -1.

The ID of the first item must be 0.

Using the example discussed above, this would be a valid list:

```
[
   [0, 'water', -1, -1],
   [1, 'container', -1, -1],
   [3, 'basin', 0, -1],
   [4, 'stream', 0, -1],
   [5, 'basketry', 1, -1],
   [6, 'vessel', 1, -1],
   [7, 'box', 1, -1],
   [8, 'sea', 0, 3],
   [9, 'ocean', 0, 3],
   [10, 'lake', 0, 3],
   [11, 'pond', 0, 3],
   [12, 'river', 0, 4],
   [13, 'wadi', 0, 4],
   [14, 'creek', 0, 4],
   [15, 'basket', 1, 5],
   [16, 'creel', 1, 5],
   [17, 'pannier, 1, 5],
   [19, 'bottle', 1, 6],
   [20, 'jar', 1, 6],
   [21, 'jug', 1, 6],
   [22, 'amphore', 1, 6],
   [23, 'coffer', 1, 7],
   [24, 'crate', 1, 7],
   [25, 'chest', 1, 7]
]
```

The ASeT project provides a concept lists which has only two semantic levels, and which is based on the Semantic fields (= Level 1) and concept names (= Level 2) provided by the (Concepticon)[https://concepticon.clld.org/parameters] project. The phrasing of some entries has been slightly modified to improve readability by the algorithm (e.g., the semantic field "emotions and values" has been modified into "emotion values" removing the connecting word "and"). It can be downloaded from the GitHub repository: [Concept List](/conceptList/ConcepticonList)

#### Lexical list

The lexical list provides the target words that need to be tagged.

The format is, once again, a list of lists, in which each item has the following form:

```
[ID_Word(int), translation(string), [form_1(string), form_2(string), etc]]
```

the translation entry must be a single string. If more translations are possible, they most be divided by a comma. Connecting words ("and", "of", "to", etc.), articles ("the", "a", "an") and other semantically empty terms should be avoided to avoid introducing "noise" that may reduce the performances of the algorithm.

The forms, instead, are input as individual entries in a list of strings.

The following is a valid example (using a small set of Italian words, with IPA transcriptions for the form entries):

```
[
   [0, 'mouse', ['tɔpo']],
   [1, 'garlic', ['aʎʎo']],
   [2, 'obey, abide, carry out', ['ubbidire', 'obbedire'],
   [3, 'bread', ['pane']]
]
```

## Arguments

The algorithm takes the following arguments:

* **json_semanticSelection_One : string** - First semantically tagged lexical list -- Format: json string - output of the ASeT algorithm
* **json_semanticSelection_Two : string** - Second semantically tagged lexical list -- Format: json string - output of the ASeT algorithm
* **pathModel : string** - Path to the semantic model. The path must include the path name of the model itself, in the format "folder1/folder2/NameModel
* **pathOutput : string** - Path to save the results (string - no extension; e.g. /my/folder/name_file_with_my_results)

The follwoing arguments are optional:

* **scoreAlignPhon : string** - Select type of score according to which the phonetic alignments are organized
-- default: "09_Aver_Score_Sem-Phon_Corr"  
-- options: "07_Sim_Score_Phon_Corr_Match", "08_Sim_Score_Phon_Glob_Match", "09_Aver_Score_Sem-Phon_Corr", or "10_Aver_Score_Sem-Phon_Glob"
-- "07_Sim_Score_Phon_Corr_Match" uses the function "(((SumFeat) / (NrFeat * 7.71)) / (LenAlign * 4.77117)"
-- "09_Aver_Score_Sem-Phon_Corr" is the average between the semantic score and the "07_Sim_Score_Phon_Corr_Match"
-- "10_Aver_Score_Sem-Phon_Glob" is the average between the semantic score and the "08_Sim_Score_Phon_Glob_Match"
-- see FAAL documentation for details ( https://github.com/MKilani/FAAL )
* **verbose : Boolean** - Print logs while executing -- Default: True
* **semanticLevel : string** - Level of the semantic tags according to which the comparison is performed. The options, for now, are: "Level_01", "Level_02", "Level_03" (see ASeT algorithm for details)
* **dividers : [ ]** - Dividers to be used to split meanings, if the previous option is set to True -- Default: [","]
* **selectBest : string** - Parameter according to which the algorithm selects the best matches among those identified by the ALeA on the basis of the other parameters
-- default: "07_Sim_Score_Phon_Corr_Match"
-- options: "07_Sim_Score_Phon_Corr_Match", "08_Sim_Score_Phon_Glob_Match", "09_Aver_Score_Sem-Phon_Corr", or "10_Aver_Score_Sem-Phon_Glob"
-- "07_Sim_Score_Phon_Corr_Match" uses the function "(((SumFeat) / (NrFeat * 7.71)) / (LenAlign * 4.77117)"
-- "09_Aver_Score_Sem-Phon_Corr" is the average between the semantic score and the "07_Sim_Score_Phon_Corr_Match"
-- "10_Aver_Score_Sem-Phon_Glob" is the average between the semantic score and the "08_Sim_Score_Phon_Glob_Match"
-- see FAAL documentation for details ( https://github.com/MKilani/FAAL )
* **selectBestThreshold: string** - Threshold for the parameter selectBest -- default: 0.65
* **parseVow: Boolean** - This allows to decide if the phonetic comparison should take into consideration vowels or not. Ignoring vowels can be useful when dealing with unrelated or relatively distant languages, or with languages in which vowels are rather unstable and semantically secondary (e.g. Semitic languages) -- default: True



## Output

The algorithm yields three outputs, therefore three variable separated by commas are needed to store the results:

```python
json_semanticSelectionDict, json_semanticSelectionDict_best, semanticSelectionDict_best_simplified = ALeA(json_semanticSelection_One, json_semanticSelection_Two, pathModel, scoreAlignPhon = "09_Aver_Score_Sem-Phon_Corr", verbose = False, semanticLevel = "Level_02", dividers = [","], selectBest = "07_Sim_Score_Phon_Corr_Match", selectBestThreshold = 0.65, parseVow = True)
```

The first output is a nested dictionary (in json format) with all the matches that fits the given parameters. The second output, instead, is selection of the matches that have a score of phonemic similarity that is higher than the **phoneticThreshold** argument.

The format of the first two outputs is the following:

```python
{
   "0": {                                                 # ID entry - index for the following data
      "0": {                                              # Semantic Cluster of the match
         "00_ID_token": int,                               # ID item lexical list A
         "01_Meaning_token": string,                       # Meaning(s) item lexical list A
         "02_Form_token": [                                # Form(s) item lexical list A - spelled in IPA
            string,
            string
         ],
         "03_Matches": {                                  # Organized matches from lexical list B - index for the matches
            "Level_XX": {                                 # Level of the semantic tags used in the comparison - XX = 01, 02 etc                        
               "0": {                                     # ID match
                  "00_ID_Match": int,                      # ID item from lexical list B
                  "01_Meaning_Match": string,              # Meaning(s) item lexical list B
                  "02_Form_Match": [                       # Form(s) item lexical list B - spelled in IPA
                     string,
                     string
                  ],
                  "03_Best_Match_Sem": [                   # Meanings of items list A and B with highest semantic similarity
                     string,
                     string
                  ],
                  "04_Best_Match_Phon": [                  # Forms of items list A and B with highest phonetic similarity
                     int,
                     string,
                     int,
                     string
                  ],
                  "05_ID_Cluster": int,                   # Semantic Cluster of the match
                  "06_Sim_Score_Sem_Match": float,         # Semantic similarity item list A - item list B
                  "07_Sim_Score_Phon_Corr_Match": float,   # Phonetic alignemnt - Corrected similarity score (see FAAL documentation)
                  "08_Sim_Score_Phon_Glob_Match": float,   # Phonetic alignemnt - Global similarity score (see FAAL documentation)
                  "09_Aver_Score_Sem-Phon_Corr": float,   # Phonetic-Semantic alignemnt - Average Corrected similarity score - Semantic score
                  "10_Aver_Score_Sem-Phon_Glob": float,   # Phonetic-Semantic alignemnt - Average Global similarity score - Semantic score
                  "11_Semantic_Field": string,            # Matching semantic tag
                  "12_ResultsComp": {
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
         }
      }
   },
   etc.
}
```

The third output is a list of dictionaries with a summary of the results with only the most relevant informations. Each entry represent a semantic tag, and it contains the following fields:

```
"01_Entry_ID" : ID of the word in list A.
"02_Entry_Form" : Form of the word in list A.
"03_Entry_Meaning" : Meaning of the word in list A.
"04_Match_ID" : ID of the match from list B.
"05_Match_Form" : Form of the match from list B.
"06_Match_Meaning" : ID of the match from list B.
"07_Selecting_Score_Best" : Score used to select the best matches.
```
