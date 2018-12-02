#input is a list of prospective aspects.
import numpy as np
from collections import OrderedDict
import pandas as pd
import re


def getParent(i, cluster):
    if(cluster[i]== i):
        return i
    return getParent(cluster[i], cluster)



def doesexist(aspectset, cluster, delta):
    for i in range(len(aspectset)-1):
        for j in range(i+1, len(aspectset)):
            if(getParent(i, cluster)!= getParent(j, cluster) and getDistance(aspectset[i], aspectset[j], cluster)<= delta):
                return True

    return False



def select(aspectset, cluster, delta, rank):
    min= delta
    suspect= []
    for i in range(len(aspectset)-1):
        for j in range(i+1, len(aspectset)):
            a= getDistance(aspectset[i], aspectset[j], cluster)
            if (getParent(i, cluster)!= getParent(j, cluster) and a<= min):
                min= a
                suspect= []#clear earlier storages
                suspect.append(i)
                suspect.append(j)

    if(rank[getParent(suspect[0], cluster)]>= rank[getParent(suspect[1], cluster)]):
        cluster[getParent(suspect[1], cluster)]= cluster[getParent(suspect[0], cluster)]#merging the clusters
        rank[getParent(suspect[0], cluster)]+= rank[getParent(suspect[1], cluster)]
    else:
        cluster[getParent(suspect[0], cluster)] = cluster[getParent(suspect[1], cluster)]
        rank[getParent(suspect[1], cluster)]+= rank[getParent(suspect[0], cluster)]#updating the ranks

    return



def select2(aspect, aspectset, cluster, delta, rank, rank2, count):#no need of rank for this case
    min= delta#what if all are farther than delta?
    index= -1
    count2= 0
    aspect= aspect[count]
    for word in aspectset:
        a= getDistance(aspect, word, cluster)
        if(a< min):
            min= a
            index= count2
        count2+= 1

    if(index!= -1):
        cluster[count]= cluster[getParent(index, cluster)]
        rank[getParent(index, cluster)]+= rank2[count]



def cluster(aspects, k, s, delta):
    aspects= sorted(aspects.items(), key= lambda x: x[1], reverse= True)
    aspectset= []
    rank= []
    count= 0
    for tuple in aspects:
        if(count== s):
            break
        aspectset.append(tuple[0])
        rank.append(tuple[1])#storing frequency to compute biased unions while clustering.
        count+= 1

    count= 0
    aspectset2= []
    rank2= []
    for tuple in aspects:
        if(count>= s):
            aspectset2.append(tuple[0])
            rank2.append(tuple[1])
        count+= 1


    print (aspectset) #as a check
    cluster= np.arange(len(aspects))

    while (doesexist(aspectset, cluster, delta)):
        select(aspectset, cluster, delta, rank)

    count= 0
    for aspect in aspectset2:
        select2(aspect, aspectset, cluster, delta, rank, count)
        count+= 1

    topclusters= {}
    for i in range(len(aspects)):
        if(aspects[getParent(i, cluster)][0] in topclusters):
            topclusters[aspects[getParent(i, cluster)][0]]+= aspects[i][1]
        else:
            topclusters[aspects[getParent(i, cluster)][0]]= aspects[i][1]

    return sorted(topclusters.items(), key= lambda x: x[1], reverse= True)
