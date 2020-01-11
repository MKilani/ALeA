# ALeA : Automatic Lexical Aligner 

Version: 0.0.1

Status: Beta

Release date: 08.01.2020

#### Authors

* **Marwan Kilani** - Swiss National Science Foundation (Mobility Grant) - Freie Universität Berlin (2019-2020)

#### How to cite

Kilani Marwan, 2020, ALeA : Automatic Lexical Aligner, https://github.com/MKilani/ALeA

## Introduction

Note: for a detailed explaination of the functioning of ASeT, see Kilani forthcoming. What follows here is just a short summary of the functioning of the algorithm.

ASeT is a python library that, given two lists of words List_A and List_B, automatically identify the semantically and phonemically most similar words in List_B for each word in List_A. ASeT can be used for multiple purposes. For instance, it can be used to align lexical lists (e.g. different dictioanries for a same language), to identify related words within a given lexical list (by comparing the list with itself), to identify cognates in lexical lists of different but related languages, or between different stages of the same language, or to identify loanwords and shared wanderwords in lexical lists of unrelated languages.

The algorithm can be used with any language, as long as translations in a same single "bridge" language (e.g. English) is provided for each word in each list. The semantic analysis will be performed through this "bridge language".

The algorithm procedes in two steps, first alignign the words semantically, and then alignign phoentically each word that has been identified as sematnically compatible. More in particular:

* First, each word in each list is analysed semantically, and is labelled with a series of semantic tags describing their sementic fields. This process of semantic tagging is performed fully automatically, using the ASeT algorithm. For details, see the ASeT github repository here: https://github.com/MKilani/ASeT

* Second, the algorithm semantically matches each word of List_A with each word of List_B, by looking in List_B for any word that share the same semantic tags of the target word in List_A. In this way, each word of List_A is matched with a selection of semantically compatible words from List_B. After that, the algorithm compares the phonological form of each word of List_A with the form of each semantically compatible word from List_B, looking for the phonologically more similar pair. This phonological comparison is also performed automatically, using the aligning algorithm FAAL. For details, see the FAAL github repository here: https://github.com/MKilani/FAAL and [Kilani 2020]().

The result of this process is a is a combined list, in which each word of List_A is associated with selection of semantically compatible words from List_B, organized according to their phonological similarity.

It has to be stressed that obviously, the best results are obtained when this method is used as a semi-automatic approach, where the results of the automatic matching process are manually verified to eliminate possible spurious tags.

## Getting Started

### Prerequisites

You need Python 3.

### Installing

The python package can be installed through pip:

```shell
python3 pip ALeA
```

ALeA is called through the method xxx() . Here a minimal working example:

```python
xxx
```

## Input

The algorithm requires the following items:

#### Lexical List A and Lexical List B

The lexical lists provide the words that need to be compared and aligned.

The format is a list of lists, in which each item has the following form:

```
[ID_Word(int), translation(string), [form_1(string), form_2(string), etc]]
```

The translation entry must be a single string. If more translations are possible, they must be separated by a comma ','. Other separators can be declared explicitely (see below). Connecting words ("and", "of", "to", etc.), articles ("the", "a", "an") and other semantically empty terms should be avoided to avoid introducing "noise" that may reduce the performances of the algorithm.

The forms, instead, are individual entries in a list of strings. They must be transcribed un IPA in unicode to be correctly processed by FAAL (see https://github.com/MKilani/FAAL and [Kilani 2020]() for details)

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

The word2vec pre-trained model GoogleNews-vectors-negative300 can be used - it can be downlaod from this github repository: https://github.com/mmihaltz/word2vec-GoogleNews-vectors

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

The ASeT project provides a concept lists which has only two semantic levels, and which is based on the Semantic fields (= Level 1) and concept names (= Level 2) provided by the (Concepticon)[https://concepticon.clld.org/parameters] project. The phrasing of some entries has been slightly modified to improve readability by the algorithm (e.g., the semantic field "emotions and values" has been modified into "emodion values" removing the connecting word "and"). It can be downlaoded from the github repository: [Concept List](/conceptList/ConcepticonList)

#### Lexical list

The lexial list provides the targed words that need to be tagged.

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

xxx




The algorithm takes the following arguments:

* **LexicalList : [ [] ]** - List of words to be tagged (see above).
* **SemanticTags : [ [] ]** - List of semantic tags
* **pathModel : string** - path to the semantic model. The path must include the path name of the model itself, in the format "folder1/folder2/NameModel.
* **pathSemanticOutput : string** - path to the location where to save the output of ASeT. The path must include the path name of the model itself, in the format "folder1/folder2/NameOfOutput.

The follwoing arguments are optional:

* **numberMatchesOutput : int** - gensim allows to limits the number of best outputs when calculating semantic distances using a WmdSimilarity function ( which is the one used by ASeT - see [gensim.similarities.WmdSimilarity](https://tedboy.github.io/nlps/generated/generated/gensim.similarities.WmdSimilarity.html) ) . With None, no limit is appliaed. Default: None
* **semanticThreshold : double** - in case one wants to add a semantic threshold to limit the numebr of matches in addition to the clustering method, it can be set here. Default: 0.00 (= no threshold)
* **verbose : boolean** - Print logs while executing. Default: False
* **splitMenings : boolean** - Option to split meanings (like in the case of entry 2 'obey, abide, carry out' in the example above). Default: True
* **dividers : [ ]** - Dividers to be used to split meanings, if the previous option is set to True. Default: [","]
* **thresholdClusters_lvl1** - Number of most similar clusters to be retained from Level 1 - Default: 2
* **thresholdClusters_lvl2** - . Default: 2
* **thresholdClusters_lvl3** - . Default: 2

Concernign the last three arguments, note that the first cluster corresponds to semantic tags that have a 1.0 semantic distance from the target word, i.e. semantic tags that are perceived by the algorithm as identical with the target word itself (e.g. the semantic tag "water" in comparison with the target word "water"). If no semantic tag has a 1.0 semantic distance with the target word, i.e. if no sematic tag has a fully matches the target word, then the first cluster will be empty. For this reason, it is reasonable to always select at least the first 2 clusters.

## Output

Coming soon.

## Example

Coming soon.

## Running the tests

Coming soon.





