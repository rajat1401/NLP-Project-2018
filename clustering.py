#input is a list of prospective aspects.
import numpy as np
import pickle
import spacy
from similarity import getDistance2, getDistance#this is not working prolly. fix this shit
from collections import OrderedDict
import pandas as pd
import re



#gets the index of the parent of the element at a given index
def getParent(i, cluster):
    if(cluster[i]== i):
        return i
    return getParent(cluster[i], cluster)



#there exists a pair to add to the cluster
def doesexist(aspectset, aspects, cluster, delta, nlp, matrixg, matrixt):
    for i in range(len(aspectset)-1):
        for j in range(i+1, len(aspectset)):
            print (i, j)
            if(cluster[getParent(i, cluster)]!= cluster[getParent(j, cluster)] and getDistance(aspectset[i], aspectset[j], nlp)<= delta):
                return True

    return False



#clustering within the seed clusters and ranking
def select(aspectset, aspects, cluster, delta, rank, nlp, matrixg, matrixt):
    min= delta
    suspect= []
    print('select enter')
    for i in range(len(aspectset)-1):
        for j in range(i+1, len(aspectset)):
            print(i, j)
            a= getDistance(aspectset[i], aspectset[j], nlp)
            if (cluster[getParent(i, cluster)]!= cluster[getParent(j, cluster)] and a< min):
                min= a
                suspect= []#clear earlier storages
                suspect.append(i)
                suspect.append(j)

    if(rank[getParent(suspect[0], cluster)]>= rank[getParent(suspect[1], cluster)]):
        # updating the ranks
        rank[getParent(suspect[0], cluster)]+= rank[getParent(suspect[1], cluster)]
        # merging the clusters
        cluster[getParent(suspect[1], cluster)]= cluster[getParent(suspect[0], cluster)]
    else:
        rank[getParent(suspect[1], cluster)]+= rank[getParent(suspect[0], cluster)]
        cluster[getParent(suspect[0], cluster)]= cluster[getParent(suspect[1], cluster)]

    return



#clustering outside of seed clusters
def select2(aspect, aspectset, aspects, cluster, delta, rank, rank2, count, nlp, matrixg, matrixt):#no need of rank for this case
    min= delta#what if all are farther than delta?
    index= -1
    count2= 0
    for word in aspectset:
        a= getDistance(aspect, word, nlp)
        if(a< min):
            min= a
            index= count2
        count2+= 1

    if(index!= -1):
        rank[getParent(index, cluster)]+= rank2[count]
        cluster[count+len(rank)]= cluster[getParent(index, cluster)]



#make sure s greater than k. return final clusters!
def cluster(aspects, k, s, delta):
    aspects= sorted(aspects.items(), key= lambda x: abs(x[1][0]) + abs(x[1][1]), reverse= True)
    nlp= spacy.load('en_core_web_md')
    with open('matrixg.pickle', 'rb') as f:
        matrixg = pickle.load(f)
    with open('matrixt.pickle', 'rb') as f:
        matrixt = pickle.load(f)

    #sorted by the most talked about aspects
    aspectset= []
    aspectset2 = []
    rank= []
    rank2 = []
    count= 0
    for tuple in aspects:
        if(count< s):
            aspectset.append(tuple[0])
            rank.append(abs(tuple[1][0]) + abs(tuple[1][1]))#storing frequency to compute biased unions while clustering.
        else:
            aspectset2.append(tuple[0])
            rank2.append(abs(tuple[1][0]) + abs(tuple[1][1]))
        count+= 1

    print (len(aspectset)) #as a check
    print (len(aspectset2))
    cluster= np.arange(len(aspects))

    print('while starts')
    while (doesexist(aspectset, aspects, cluster, delta, nlp, matrixg, matrixt)):
        select(aspectset, aspects, cluster, delta, rank, nlp, matrixg, matrixt)


    count= 0
    for aspect in aspectset2:
        select2(aspect, aspectset, aspects, cluster, delta, rank, rank2, count, nlp, matrixg, matrixt)
        count+= 1


    freqdict= {}
    for i in range(len(rank)):
        a= getParent(i, cluster)
        if(aspectset[a] not in freqdict):
            revs= [0, 0]
            for j in range(len(cluster)):
                if(cluster[j]== a):
                    revs[0]+= aspects[j][1][0]
                    revs[1]+= aspects[j][1][1]
            freqdict[aspectset[a]]= revs


    freqdict= sorted(freqdict.items(), key= lambda x: x[1], reverse= True)
    return freqdict[:min(k, len(freqdict))]#dont return this now. again coreference this with cluster and then return



with open('suspects.pickle', 'rb') as f:
    suspect= pickle.load(f)

print (len(suspect))
print (cluster(suspect, 10, 25, 0.49))