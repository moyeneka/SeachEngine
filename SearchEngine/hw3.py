# Information Retrieval Homework 3
# Author: Brian Roden
# Modified By: Sebastian Canales
# Program to parse html files for tokens

import hashtable
import ply.lex as lex
import sys
import re
import os
from collections import Counter
import math

TOKEN_SIZE = 14
DOCS_SIZE = 3
START_SIZE = 7
FREQ_SIZE = 4
NAME_SIZE = 11

# Writing records
def writeDictRecord(f, token, numDocs, start):
    #write truncated token and justify to the right
    f.write(token[0:min(len(token), TOKEN_SIZE)].rjust(TOKEN_SIZE))
    f.write(' ')

    #write numDocs and justify to right
    tempNum = min(numDocs,(int)(pow(10, DOCS_SIZE)-1))
    f.write(str(tempNum).rjust(DOCS_SIZE))
    f.write(' ')

    #write start num and justify to right
    tempNum = min(start, (int)(pow(10, START_SIZE)-1))
    f.write(str(tempNum).rjust(START_SIZE))

    f.write("\n")

def writePostRecord(f, docID, freq):
    #write docID and justify right
    tempNum = min(docID,(int)(pow(10, DOCS_SIZE)-1))
    f.write(str(tempNum).rjust(DOCS_SIZE))
    f.write(' ')

    #write freq and justify right
    tempNum = min(freq, (int)(pow(10, FREQ_SIZE)-1))
    if tempNum < 1:
        tempNum = 1
    else:
        tempNum = int(tempNum)
    f.write(str(tempNum).rjust(FREQ_SIZE))
    f.write("\n")

def writeMapRecord(f, name):
    #write truncated file name and justify to right
    f.write(name[0:min(len(name), NAME_SIZE)].rjust(NAME_SIZE))
    f.write("\n")

def weightCalc(freq, docTokens, docNum, termDocs):
    weight = freq/docTokens * (1 + math.log10(docNum/termDocs)) * 1000000
    weight = int(weight)
    return weight

# List of token types
tokens = (
    'CSS',
    'HTMLTAG',
    'HYPERLINK',
    'EMAIL',
    'NUMBER',
    'HTML_ENTITY',
    'WORD',
)

# CSS Tags take the form: element1, element2, .. elementN { ** CSS ** }
# Regex Checks for any amount of words with a comma, followed by another word, followed by { ** CSS ** }
# No return statement because these are not useful for indexing
def t_CSS(T):
    r'([\S^,]*,\s*)*\S+\s*{[^}]+}'

# HTML Elements take the forms <! **** COMMENT / DOCTYPE ****>, or <WORD attribute1=value attribute2=value>, or </WORD>
# Regex first checks for a "<", then first checks if there is a "!" character, in which case it will read until the next ">", since these are either comments or DOCTYPE declarations.
# If no "!", it will look for "<" followed by an optional "/", followd by WORD, followed by any amount of "attribute=value", followed by optional whitespace, then ">"
# No return statement because these are not useful for indexing
def t_HTMLTAG(t):
    r'<(![^>]+|\/?\w+((\s*[^\s=>])+=(\s*[^\s=>])+)*\s*\/?)>'

# Regex checks for hyperlinks, which are words starting with http://, https://, or www., and any number of non-whitespace, html tags, or "/" is found (since including the specific subdirectory of the site is not useful for indexing)
# The starting elements are then scrubbed out
def t_HYPERLINK(t):
    r'(htt(p|ps):\/\/|www.)[^\s<\/]+'
    t.value = t.value.lower()
    t.value = re.sub(r'(https://|http://|www|\.)', '', t.value)
    return t

# Regex to check for emails, which take the form "word@word.word"
# HTML tags and everything following @ is removed since searching for "gmail" to get a specific email address is unlikely
def t_EMAIL(t):
    r'\S+@\S+\.[^<\s,?!.\xa0\x85]+'
    t.value = re.sub('(@.*|<[^>]+>)', '', t.value)
    return t

# Regex to check for numbers, which include commas, decimals, and hyphens for phone numbers
# Will not start with 0 since "01" and "1" should be the same in searches. Commas and hyphens are removed, as well as everything following the decimal since a search for "20.07" specifically would likely not be useful
def t_NUMBER(t):
    r'[1-9](\d|,|\.|-)*'
    t.value = re.sub('(,|-|\.\S*)', '', t.value)
    return t

# Regex to remove common html entities like "&nbsp" which the parser was otherwise unable to detect
# No return statement because these are not useful for indexing
def t_HTML_ENTITY(t):
    r'\&\w+'

# Words are similar to typical IDs, exxcept with special inclusions for allowing specific punctuation so tokens don't become improperly split.
# These start with a A-z character, and can be followed by more characters, digits, hyphens, apostrophes, html tags, and periods for abbreviations like "PH.D"
# These additions are included since "we'll" won't become "we" and "ll" separately, nor "<b>E</b>lephants" becoming "e" and "lephants". These are then removed with the re.sub expression to make for better indexing
# Other punctuation marks, like ?, !, etc. are not typically connecting words together, so these are not included
def t_WORD(t):
    r'[A-z](\w|\'|-|\.\w|<[^>]+>)*'
    t.value = t.value.lower()
    t.value = re.sub('(\.|-|\'|<[^>]+>)', '', t.value)
    return t

# Tracks line numbers with \n. Mostly for debugging purposes, but it's inclusion does not hurt performance.
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# Ignore these characters if they are not already a token. Improves performance since these won't have to be passed through the regex rules.
t_ignore  = ' []+$|=%*{}/0-"#>();:!?.,\t\xa0\x85\xe2\x00'

# Skips letters that fail all token checks. Punctuation like & and < will use this a lot: they cannot be included in t_ignore since they are required for the start of some regex rules.
def t_error(t):
    t.lexer.skip(1)

# Create the parser
lexer = lex.lex()

# Open file directories
indir = os.path.abspath(sys.argv[1])
outdir = os.path.abspath(sys.argv[2])
if not os.path.isdir(indir):
    print("Error: invalid input path")
    exit()
if not os.path.isdir(outdir):
    print("Error: invalid output path")
    exit()
try:
    dictFile = open("{}/dict".format(outdir), 'w')
    postFile = open("{}/post".format(outdir), 'w')
    mapFile = open("{}/map".format(outdir), 'w')
except Exception as e:
    print("Error opening output files: {}", str(e))
    exit()

# Initialize values
totalTokens = 0 
docID = 0
DOC_HT_SIZE = 50000
GLOB_HT_SIZE = 350000
STOPWORD_SIZE = 2208
docHT = hashtable.HashTable(DOC_HT_SIZE)
globHT = hashtable.GlobalHashTable(GLOB_HT_SIZE)
swHT = hashtable.HashTable(STOPWORD_SIZE)

tokensInDoc = []
# Insert into sw hash table
with open("{}/{}".format(outdir, "stopwords.txt"), 'r', encoding="latin-1") as file:
    lines = file.readlines()
    for line in lines:
        line = line.rstrip('\n')
        swHT.insert(line, 1)

#Tokenize and insert into other Hash Tables
for i in os.listdir(indir):
    # Open current input file
    try:
        data = open("{}/{}".format(indir, i), 'r', encoding="latin-1").read()
        lexer.input(data)
    except Exception as e:
        print("Error opening file {}: {}".format(), i, str(e))
        continue

    # Read tokens and add them to document hashTable
    docTokens = 0
    while True:
        tok = lexer.token()
        if not tok:
            break
        #check if present in stop word HT
        present = swHT.intable(tok.value)
        #if token is bigger than 1 char and not present in stopwords, insert
        if len(tok.value) > 1 and present == False:
            docHT.insert(tok.value, 1)
            docTokens += 1
    # Write doc HT to global HT, reset docHT, and write filename to map file
    for j in range(DOC_HT_SIZE):
        if docHT.slots[j] is not None and docHT.data[j] != 0:
            globHT.insert(docHT.slots[j], (docID, docHT.data[j]))
    tokensInDoc.append(docTokens)
    print(str(i) + ": " + str(docTokens) + "\n")
    docHT.reset()
    # mapFile.write("{}\n".format(i))
    writeMapRecord(mapFile, i)
    docID += 1


# Write all entries to the dict and hash files
postLineNo = 0
for i in range(GLOB_HT_SIZE):
    if globHT.slots[i] is not None and globHT.data[i] is not None:
        if globHT.data[i].numDocs == 1 and globHT.data[i].files[0][1] == 1:
            writeDictRecord(dictFile, "REMOVED", -1, -1)
        else:
            #dictFile.write("{}:{:n}:{:n}\n".format(globHT.slots[i], globHT.data[i].numDocs, postLineNo))
            writeDictRecord(dictFile, globHT.slots[i], globHT.data[i].numDocs, postLineNo)
            totalfreq = 0
            for j in globHT.data[i].files:
                # postFile.write("{:n}:{:n}\n".format(j[0], j[1]))
                weight = weightCalc(j[1], tokensInDoc[j[0]], docID, globHT.data[i].numDocs)
                # writePostRecord(postFile, j[0], weight)
                writePostRecord(postFile, j[0], j[1])
                postLineNo += 1
    else:
        #dictFile.write("NULL:-1:-1\n")
        writeDictRecord(dictFile, "NULL", -1, -1)