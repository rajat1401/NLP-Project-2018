import numpy as np
import math
import spacy
import pickle
import nltk



def getParent(i, cluster):
    if(cluster[i]== i):
        return i

    return getParent(cluster[i], cluster)



#cosine similarity function
def cosine_similarity(vector1, vector2):
    score= np.dot(vector1, vector2)/((np.linalg.norm(vector1))*(np.linalg.norm(vector2)))
    return score



#gives distance using wordnet similarity(cafe-g)
def getDistance1(aspect1, aspect2, nlp):
    #nlp= spacy.load('en_core_web_md')
    doc1= nlp(aspect1)
    doc2= nlp(aspect2)
    token1= doc1[0]
    token2= doc2[0]
    return (1 - token1.similarity(token2))



#cafe-t
def getDistance2(aspect1, aspect2, aspects, matrixg, matrixt):
    index1 = 0
    index2 = 0
    for i in range(len(aspects)):
        if (aspects[i][0] == aspect1):
            index1 = i
        if (aspects[i][0] == aspect2):
            index2 = i

    b= cosine_similarity(matrixt[index1], matrixt[index2])
    b= 1-b
    return b



#return the count of the given word in the review corpus
def getCount(word1, word2, reviews):
    count1= 0
    count2= 0
    count3= 0
    for review in reviews:
        toadd1= 0
        toadd2= 0
        if(word1 in review):
            toadd1= 1
        if(word2 in review):
            toadd2= 1
        if(toadd1== 1 and toadd2== 1):
            count3+= 1
        count1+= toadd1
        count2+= toadd2

    return (count1, count2, count3)




#reviews has list of all reviews in string form. aspects here is just sorted aspects
def buildmatrix(nlp, aspects, reviews, keys):
    print ("start")
    matrixg= np.zeros(shape= (len(aspects), len(aspects)))
    for i in range(len(aspects)):
        for j in range(len(aspects)):
            print (i, j)
            matrixg[i][j]= getDistance1(keys[i], keys[j], nlp)

    print ("matrixg is completed")
    with open('matrixg.pickle', 'wb+') as f:
        pickle.dump(matrixg, f)

    matrixt= np.zeros(shape= (len(aspects), len(aspects)))
    for i in range(len(aspects)):
        for j in range(len(aspects)):
            print (i, j)
            count1, count2, count3= getCount(keys[i], keys[j], reviews)
            count1+= 1
            count2+= 1
            count3+= 1
            a= math.log(((len(reviews)*count3)/(count1*count2)), 2)
            b= math.log((count3/len(reviews)), 2)
            matrixt[i][j]= -a/b

    print ("matrices computed bitch")
    with open('matrixt.pickle', 'wb+') as f:
        pickle.dump(matrixt, f)

    return (matrixg, matrixt)



#check
#print (getDistance('good', 'nice', 1))

#cafe-gt
def getDistance3(aspect1, aspect2, aspects, matrixg, matrixt):#aspects is a dictionary.
    #aspects= aspects[:min(100, len(aspects))]
    index1= 0
    index2= 0
    for i in range(len(aspects)):
        if(aspects[i][0]== aspect1):
            index1= i
        if(aspects[i][0]== aspect2):
            index2= i

    a= cosine_similarity(matrixg[index1], matrixg[index2])
    a= 1-a
    b= cosine_similarity(matrixt[index1], matrixt[index2])
    b= 1-b
    c= max(cosine_similarity(matrixg[index1], matrixt[index2]), cosine_similarity(matrixg[index2], matrixt[index1]))
    c= 1-c
    return ((a+b+c)/3)


# with open('reviews', 'rb') as f:
#     reviews= pickle.load(f)
# with open('suspects.pickle', 'rb') as f:
#     aspects= pickle.load(f)


# nlp= spacy.load('en_core_web_md')
# aspects= sorted(aspects.items(), key= lambda x: abs(x[1][0]) + abs(x[1][1]), reverse= True)[:250]
# keys= []
# for tuple in aspects:
#     keys.append(tuple[0])
#
# print (len(keys))
# print (len(aspects))
#matrixg, matrixt= buildmatrix(nlp, aspects, reviews, keys)


#check
#print ("The length of the matrices are: " + str(len(matrixg)) + " and "  + str(len(matrixt)))

