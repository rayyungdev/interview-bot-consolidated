import boto3
from boto3.dynamodb.conditions import Key
import sys
import pandas as pd
import json

sys.path.append('./bot_model')
csv_location = './bot_model/data/answers.csv'
ID = '52caf274-5756-41f4-96f5-ec7a4be14cf8'



def update_data(data):
    client = boto3.resource('dynamodb')
    table = client.Table('AnswersTable')

    KEY = data.pop("ID")
    # EMAIL = data.pop("EMAIL")
    update_expression = 'SET {}'.format(','.join(f'#{k}=:{k}' for k in data))
    expression_attribute_values = {f':{k}': v for k, v in data.items()}
    expression_attribute_names = {f'#{k}': k for k in data}

    response = table.update_item(
        Key = {"ID" : KEY},  
        UpdateExpression=update_expression,
        ExpressionAttributeValues=expression_attribute_values,
        ExpressionAttributeNames=expression_attribute_names,
        ReturnValues='UPDATED_NEW', 
    )
    return response

def create_user(data):
    client = boto3.resource('dynamodb')
    table = client.Table('AnswersTable')
    try: 
        table.put_item(
            Item = data
        )
        return 200
    except Exception as e:
        print(e)
        return 400

def retrieve_name(ID): 
    client = boto3.resource('dynamodb')
    table = client.Table('AnswersTable')
    item = table.query(
        KeyConditionExpression = Key('ID').eq(ID)
    )

    if len(item['Items']) == 0:
        return None
    return item['Items'][0]['NAME']

def get_answers(ID): 
    client = boto3.resource('dynamodb')
    table = client.Table('AnswersTable')
    item = table.get_item(
        Key = {
            'ID' : ID
        }
    )
    return item['Item']

# data = get_answers(ID, NAME)

if __name__=="__main__":
    NAME = "Raymond Bot"
    testing_info = {
        'ID': ID,
        'NAME' : "Raymond-Bot"
    }

    df = pd.read_csv(csv_location, usecols = [0,2])
    df['intent'] = df['intent'].astype(str)
    df =df.set_index('intent')['response']
    testing_info.update(df.to_dict())
    testing_info.update({
        "999": "Ah it seems like you asked me something that I was not prepared to answer!\nIf you think I should have a better response for this, let me know by labeling it as misclassified"}
    )
    update_data(testing_info)
    # data = retrieve_name(ID)
    # data = get_answers(ID, NAME)
    # print(data)
    # print(data)

