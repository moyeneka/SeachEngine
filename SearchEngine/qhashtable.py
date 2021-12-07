# Created by Ang Li
# October 2, 2016
# Modified by Marion Chiariglione
# September 22, 2018
import hashlib
from collections import deque


class HashTable:
    def __init__(self, table_size):
        self.size=table_size # size of hash table
        self.uniqueTokens=0
        self.slots=[None]*self.size # initialize keys
        self.data=[None]*self.size # initialize values
    
    def reset(self): # reset keys without creating new HT
        self.uniqueTokens=0
        self.slots=[None]*self.size # initialize keys
    
    def hashfunction(self,key): # hash function to find the location
        h = hashlib.sha1() # any other algorithm found in hashlib.algorithms_guaranteed can be used here
        h.update(bytes(key, encoding="latin-1"))
        return int(h.hexdigest(), 16)%self.size

    def rehash(self, oldhash): # called when index collision happens, using linear probing
        return (oldhash+3)%self.size

    def insert(self, key, data): # insert k,v to the hash table
        hashvalue = self.hashfunction(key)  # location to insert
        if self.slots[hashvalue] == None:
            self.slots[hashvalue] = key
            self.data[hashvalue] = data
            self.uniqueTokens += 1
        else:
            if self.slots[hashvalue] == key:  # key already exists, update the value
                self.data[hashvalue] += 1
            else:
                nextslot=self.rehash(hashvalue) # index collision, using linear probing to find the location
                if self.slots[nextslot] == None:
                    self.slots[nextslot] = key
                    self.data[nextslot] = data
                    self.uniqueTokens += 1
                elif self.slots[nextslot] == key:
                    self.data[nextslot] += 1
                else:
                    while self.slots[nextslot] != None and self.slots[nextslot] != key:
                        nextslot=self.rehash(nextslot)
                        if self.slots[nextslot] == None:
                            self.slots[nextslot] = key
                            self.data[nextslot] = data
                            self.uniqueTokens += 1

                        elif self.slots[nextslot] == key:
                            self.data[nextslot] += 1

    def get(self, key):  # get the value by looking for the key
        startslot = self.hashfunction(key)
        data = None
        stop = False
        found = False
        position = startslot
        while self.slots[position] != None and not found and not stop:
            if self.slots[position] == key:
                found = True
                data = self.data[position]
            else:
                position=self.rehash(position)
                if position == startslot:
                    stop = True
        return data

    def intable(self, key):  # determine whether a key is in the hash table or not
        startslot = self.hashfunction(key)
        stop = False
        found = False
        position = startslot
        while self.slots[position] != None and not found and not stop:
            if self.slots[position] == key:
                found = True
            else:
                position=self.rehash(position)
                if position == startslot:
                    stop = True
        return found

    def __getitem__(self, key):
        return self.get(key)

    def __setitem__(self, key, data):
        self.insert(key,data)

    def __len__(self):
        return self.size
# Regular hashtable, except values are numDocs + Linked List pairs instead of frequency counts. Used for tracking all doc frequencies
class QueryHashTable(HashTable):
    # Pair of numDocs and Linked List for cross-file referencing
    class Entry:
        def __init__(self, data):
            self.numDocs = 1
            self.files = deque()
            self.files.append(data)

    def __init__(self, table_size):
        HashTable.__init__(self, table_size)

    
    # Override regular insert, replace frequency count with Entry class
    def insert(self, key, data): # insert k,v to the hash table
        hashvalue = self.hashfunction(key)  # location to insert
        if self.data[hashvalue] == None:
            #self.slots[hashvalue] = key
            self.data[hashvalue] = self.Entry(data)
            self.uniqueTokens += 1
        else:
            if self.data[hashvalue] == self.Entry(data):  # key already exists, update the value
                self.data[hashvalue].numDocs += 1
                self.data[hashvalue].files.append(data)

            else:
                nextslot=self.rehash(hashvalue) # index collision, using linear probing to find the location
                if self.data[hashvalue] == None:
                    #self.slots[nextslot] = key
                    self.data[nextslot] = self.Entry(data)
                    self.uniqueTokens += 1

                elif self.data[hashvalue] == self.Entry(data):
                    self.data[nextslot].numDocs += 1
                    self.data[nextslot].files.append(data)

                else:
                    while self.data[hashvalue] != None and self.data[hashvalue] != self.Entry(data):
                        nextslot=self.rehash(nextslot)
                        if self.data[hashvalue] == None:
                            #self.slots[nextslot] = key
                            self.data[nextslot] = self.Entry(data)
                            self.uniqueTokens += 1

                        elif self.data[hashvalue] == self.Entry(data):
                            self.data[nextslot].numDocs += 1
                            self.data[nextslot].files.append(data)


