# %%
fquestions = './data/questions.csv'
fanswers = './data/answers.csv'

# %%
import pandas as pd
import numpy as np

df_questions= pd.read_csv (fquestions, usecols=[0,1])
df_answers = pd.read_csv(fanswers, usecols=[0,1])

# %% [markdown]
# ### Main focus: 
#  - can't use hierarchical classification just yet --> I don't have enough data nor do I really know because I'll be making up the data. 
#    - I don't have a hierarchy for questions yet...
#       - I don't have subsections? I'll figure more about that later when I actually have a larger dataset and we can see the clusters. 
#    - Need people to test this out. When people test this out, I'll record their responses so that I will get a hierarchy of responses.
# 
# ### Building Model Facts
# #### *Jetz Schurrmans et al*
# - Methodology
#    - CBOW-SVM
#        - Continuous Bag of Words
#          - FastText Embeddings
#             - Average performed best
#                - $ CBoW_{avg}(t_1,...,t_k) = \frac{1}{k}\sum_{i=1}^{k}{v(t_i)}$
#          - other options:
#             Word2Vec, GloVe, and GPT-3 (if I even to want to try it)
#          

# %%
# How to use torchtext for fasttext encoding
# https://towardsdatascience.com/deep-learning-for-nlp-with-pytorch-and-torchtext-4f92d69052f 

# But first, let's concatenate our dataset with appropiate label, not just a num
from utils import *

df_set = df_questions.copy()
df_set['questions'] = df_set['questions'].apply(lambda x: remove_punctuation(x))
df_set['questions'] = df_set['questions'].apply(lambda x: x.lower())
df_set['intent'] = df_set['intent'].apply(lambda x: df_answers.loc[df_answers['intent']==x, 'intent_v'].item())

lengths = df_set['questions'].str.len().max() # It's 75
#So let's just set our vector size to be 100
max_length = 100### Let's just get something work, let's test it with two methods
import spacy
nlp = spacy.load('en_core_web_md')
embedding_dim = nlp.vocab.vectors_length
# print(embedding_dim)

# %%
# Encoding Sentences using spaCy NLP Model

def encode_sentences(sentences):
    n_sentences = len(sentences)
    print('Length: - ', n_sentences)

    X = np.zeros((n_sentences, embedding_dim))

    #iterate over sentences

    for idx, sentence in enumerate(sentences):
        # Pass each sentence to the NLP object to create a document
        doc = nlp(sentence)
        X[idx, :] = doc.vector
    return X


train_X = encode_sentences(df_set['questions'].to_numpy())

# %%
from sklearn.preprocessing import LabelEncoder

def label_encoding(labels):
    # Calculate the length of labels

    n_labels = len(labels)
    print('Number of labels :-',n_labels)


    # import labelencoder
    # instantiate labelencoder object
    le = LabelEncoder()
    y =le.fit_transform(labels)
    print(y[:100])
    print('Length of y :- ',y.shape)
    return y, le

train_y, le= label_encoding(df_set['intent'])

# %%
from sklearn.linear_model import SGDClassifier
from sklearn.svm import SVC

def svc_training(X,y):
    clf = SGDClassifier(loss='modified_huber')
    clf.fit(X,y)
    return clf


def svc_validation(model, X, y, le):
    y_pred = model.predict(X)
    n_correct = 0
    for i in range(len(y)):
        if y_pred[i] == y[i]:
            n_correct +=1
            # print(i, 'predicted: ', le.inverse_transform([y_pred[i]]), 'true: ', le.inverse_transform([y[i]]))
    # print('Predicted {0} out of {1} training examples'.format(n_correct, len(y)))

    return n_correct/len(y)


# %%
def encode_sentence(sentence):
    return nlp(sentence.lower()).vector.reshape(1, -1)
    
test_input = "What is the meaning of life?"
test_input = encode_sentence(test_input.lower())

result = 0
cur_iter = 1
while result < 0.98:
    model = svc_training(train_X, train_y)
    result = svc_validation(model, train_X, train_y, le)
    y_test_output = np.max(model.predict_proba(test_input))
    # print(y_test_output)
    cur_iter += 1

    if y_test_output > .5:
        result = 0

    if cur_iter%1000 == 0:
        print(result)
        print(y_test_output)
    if cur_iter > 5000:
        print("FAILED...")
        break

print('Accuracy: {0}'.format(result))
print('test: {0}'.format(y_test_output))


# %%
model_name = 'model.sav'
import pickle
pickle.dump(model, open(model_name, 'wb'))
pickle.dump(le, open('transformer.sav', 'wb'))

# %%
test = ['Tell me about yourself', 'walk me through your resume']
mp = encode_sentences(test)

PREDICTION = model.predict(mp)

# %%
le.inverse_transform(PREDICTION)

# %%



