import string
import re

def remove_punctuation(text):
    punctuationfree="".join([i for i in text if i not in string.punctuation])
    return punctuationfree

import spacy
nlp = spacy.load('en_core_web_md')

def encode_sentence(sentence):
    sentence = remove_punctuation(sentence)
    return nlp(sentence.lower()).vector.reshape(1, -1)

import pandas as pd
import numpy as np
import csv

def csv_read(fname):
    with open(fname, 'r') as f:
        temp = list(csv.reader(f, delimiter = ","))
        temp = np.asarray(temp)
    header = temp[0]
    data = temp[1:]
    data = pd.DataFrame(data = data)
    data.columns = header
    print(data.head())
    return data


if __name__ =='__main__':

    fanswers = './data/answers.csv'
    df = pd.read_csv(fanswers, encoding = 'cp437')
    print(df.loc[df['intent']==1], ['response'])