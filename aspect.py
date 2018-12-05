import os
import pickle
import pandas as pd
import nltk
from nltk.corpus import stopwords
import spacy



df= pd.read_csv('hotel_reviews.csv')
nlp= spacy.load('en_core_web_md')
stop_words= stopwords.words('english')
#nltk.download('stopwords')
reviews= []
for i in range(200):
    text= df.loc[i, 'Description']
    text= nltk.word_tokenize(text)
    text= " ".join([i for i in text if i not in stop_words])
    reviews.append(text)

print (len(reviews))
print (reviews[0])
with open('reviews', 'wb+') as f:
      pickle.dump(reviews, f)


negatives = open("./negative.txt",encoding = "ISO-8859-1")
negatives = [line.strip() for line in negatives.readlines()]
positives = open("./positive.txt",encoding = "ISO-8859-1")
positives = [line.strip() for line in positives.readlines()]
opinionwords= negatives + positives



def doit(dict, key, value):
    if(key in dict):
        if(value> 0):
            dict[key][0]+= value
        else:
            dict[key][1]+= value
    else:
        dict[key]= [0, 0]
        if(value> 0):
            dict[key][0]+= value
        else:
            dict[key][1]+= value



suspect= {}
for review in reviews:
    verdict= nlp(review)
    for sent in list(verdict.sents):
        #wordlist = nltk.word_tokenize(sent.string.lower())#check this
        for word in sent:
            #print(word, word.dep_)
            #sentiment= 0
            if(word.text in opinionwords):
                if(word.text in positives):
                    sentiment= 1
                else:
                    sentiment= -1

                if(word.dep_ == 'amod'):
                    doit(suspect, word.head.text, sentiment)
                else:
                    for child in word.children:
                        #add more weight if there is an adjective/adverb modifier
                        if((child.dep_== 'amod' or child.dep_== 'advmod') and (child.text in opinionwords)):
                            sentiment*= 1.25
                        #check for negation
                        if(child.dep_== 'neg'):
                            sentiment*= -1

                #doit(suspect, word.head.text, sentiment)

                    for child in word.children:
                        if(word.pos_== 'VERB' and child.dep_== 'dobj'):
                            doit(suspect, child.text, sentiment)
                            subchildren= []
                            conj= 0
                            for subchild in child.children:
                                if(subchild.text== 'and'):
                                    conj= 1
                                if(conj== 1 and subchild.text!= 'and'):
                                    subchildren.append(subchild.text)
                                    conj= 0
                            for subchild in subchildren:
                                doit(suspect, subchild, sentiment)

                    for child in word.head.children:
                        noun = ""
                        if ((child.dep_ == "amod") or (child.dep_ == "advmod")) and (child.text in opinionwords):
                            sentiment *= 1.5
                        # check for negation words and flip the sign of sentiment
                        if (child.dep_ == "neg"):
                            sentiment *= -1

                    for child in word.head.children:
                        noun = ""
                        if (child.pos_ == "NOUN") and (child.text not in suspect):
                            noun = child.text
                            # Check for compound nouns
                            for subchild in child.children:
                                if subchild.dep_ == "compound":
                                    noun = subchild.text + " " + noun
                            doit(suspect, noun, sentiment)
                        #debug += 1


print (len(suspect))
print ((suspect))
with open('suspects.pickle', 'wb+') as f:
     pickle.dump(suspect, f)
