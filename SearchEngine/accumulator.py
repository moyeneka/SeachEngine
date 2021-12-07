import ply.lex as lex
import sys
import re
import os
import getopt
import hashlib
import hashtable


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

#hash function for finding location
def hashfunction(key):
    h = hashlib.sha1()
    h.update(bytes(key, encoding="latin-1"))
    return int(h.hexdigest(), 16)%dict_size

#Get record at recordNum
def getRecord(f, recordNum, fileSize, recordLength, token):
    record = ""
    if recordNum >= 0 and recordNum < fileSize:
        f.seek(0,0)
        f.seek(recordLength * recordNum)
        record = f.readline()
    word, num_docs, start = record.split()
    while word != "NULL" and word != token:
        if len(record) < 1:
            f.seek(0,0)
        record = f.readline()
        word, num_docs, start = record.split()
    
    #print(record)
    return word, num_docs, start

def getFile(f, recordNum, fileSize, recordLength):
    record = ""
    if recordNum >= 0 and recordNum < fileSize:
        f.seek(0,0)
        f.seek(recordLength * recordNum)
        record = f.readline()
    return record.split()

#sizes
dict_size = 350000
post_size = 1381027
map_size = 300
dict_record_length = 27
post_record_length = 9
map_record_length = 12
ht_size = 0
dict = []

#main
query = ''
directory = ''

#get arguments
argv = sys.argv[1:]
try:
    opts, args = getopt.getopt(argv, "q:d:", ["query=", "directory="])
except getopt.error as err:
    print(str(err))
    

#reading arguments
for opt, arg in opts:
    if opt in ['-q']:
        query = arg      
    elif opt in ['-d']:
        directory = arg
#open files to read
try:
    dictFile = open("dict", 'r')
    postFile = open("post", 'r')
    mapFile = open("map", 'r')
except Exception as e:
    print("error opening files: {}", str(e))
    exit()

#tokenize query
lexer.input(query)
while True:
    tok = lexer.token()
    if not tok:
        break
    
    #get hashtable location for tokenized query
    record_num = hashfunction(tok.value)

    #read in records from dict
    word, dict_doc_num, dict_start = getRecord(dictFile, record_num, dict_size, dict_record_length, tok.value)

    #store to list to access later
    dict.append([dict_doc_num, dict_start])
    ht_size += int(dict_doc_num)

#read records into accumulator
accumulator = hashtable.QueryHashTable(3*ht_size)
for i in range(len(dict)):
    for j in range(int(dict[i][0])):
        doc_id, weight = getFile(postFile, int(dict[i][1]) + j, post_size, post_record_length)
        accumulator.insert(int(doc_id), int(weight))

non_empty = []
nonempty_slots = accumulator.getNonEmpty()
for i in range(len(nonempty_slots)):
    data = accumulator.get(nonempty_slots[i])
    non_empty.append([data, nonempty_slots[i]])

non_empty.sort(reverse = True)

length = min(10, len(non_empty))
if length < 1:
    print("No Results")
else:
    print("<div class=\"container-fluid\"> <section class=\"patient\" id=\"patient\"> <br/> <h2>" + "Query Table" + "</h2><br/>")
    print("<table class=\"table table-bordered\">")
    print("<tr>")
    print("<th scope= \"col\">DictionaryID</th>")
    print("<th scope= \"col\">Files</th>")
    print("<th scope= \"col\">Weight</th>")
    print("</tr>")
    for i in range(length):
        file_name = getFile(mapFile, int(non_empty[i][1]), map_size, map_record_length)
        print("<tr>")
        print("<td>" + str(non_empty[i][1]) + "</td>")
        print("<td><a href=http://csce.uark.edu/~moyeneka/SearchEngine/files2/" +str(file_name[0])+ ">" + str(file_name[0]) + "</a>" + "</td>")
        print("<td>" + str(non_empty[i][0]) + "</td>")
        print("</td> ")
        print("</tr>")
    print("</table></section></div></div>")

