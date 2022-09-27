import sys
import pandas as pd
import spacy
import pickle
from bot_model.utils import * 

nlp = spacy.load('en_core_web_md')


parent_name = './bot_model'
## Load Model
model = parent_name + '/final_model/model.sav'
transformer = parent_name + '/final_model/transformer.sav'
loaded_model = pickle.load(open(model, 'rb'))
loaded_transformer = pickle.load(open(transformer, 'rb'))
#########################################


fanswers = parent_name+'/data/answers.csv'
fquestions = parent_name+'/data/questions.csv'

df_answers = pd.read_csv(fanswers, encoding='cp1252')
df_questions = pd.read_csv(fquestions)
df_questions = df_questions.drop_duplicates('intent', keep = 'first')
df_questions['intent'] = df_questions['intent'].astype(str)
df_questions = df_questions.set_index('intent')['questions']



default_response ='Ah it seems like you asked me something that I was not prepared to answer!\nIf you think I should have a better response for this, let me know by labeling it as misclassified'
def question_add(data):
    misclassified_csv = parent_name + '/data/misclassified_questions.csv'
    question_data = {
        'questions': data, 
        'intent': '',
    }
    with open(misclassified_csv, 'a', newline = '\n') as f:
        writer = csv.DictWriter(f, fieldnames = ['questions', 'intent'])
        writer.writerow(question_data)

class interview_bot:
    def __init__(self) -> None:
        # We'll just use this to initialize the bot so we can just retrieve this class later
        self.model = loaded_model
        self.transformer = loaded_transformer
        self.responses = df_answers
        self.questions = df_questions

    def predict(self, n):
        try:
            n = remove_punctuation(n)
            encoded_sen = encode_sentence(n.lower())
            prob = np.max(self.model.predict_proba(encoded_sen)[0])
            if prob > 0.6:
                prediction = self.model.predict(encoded_sen)
                ypred = self.transformer.inverse_transform(prediction)
                response = self.responses.loc[self.responses['intent_v']==ypred[0]]
                ypred = str(response.intent.item())

            else: 
                ypred = "999"
    
            return ypred
        
        except Exception as e:
            error = "something happened at: ", e
            print(error)


    def respond(self, n):
        try:
            n = remove_punctuation(n)
            encoded_sen = encode_sentence(n.lower())
            prob = np.max(self.model.predict_proba(encoded_sen)[0])
            if prob > 0.6:
                prediction = self.model.predict(encoded_sen)
                ypred = self.transformer.inverse_transform(prediction)
                response = self.responses.loc[self.responses['intent_v']==ypred[0]]
                output= response.response.item(), response.intent.item()
            else: 
                output = default_response, 'DEFAULT '
            return output

        except Exception as e:
            error = "something happened at: ", e
            print(error)
            return 'Sorry, something went wrong...', e


if __name__ == '__main__':
    print('Hello, this is the Raymond Interview Bot')
    print('Please ask me some basic interview questions and I will try my best to help you\n    If no input is detected, this program will end\n')
    n = 'testing'
    while n:
        n = remove_punctuation(input(''))
        if n:
            ypred = loaded_transformer.inverse_transform(loaded_model.predict(encode_sentence(n.lower())))
            response = df_answers.loc[df_answers['intent_v']==ypred[0], 'response'].item()
            print(response, '\n')