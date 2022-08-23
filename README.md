# Interview Me Bot

The purpose of this bot is to respond to frequently asked interview questions. It uses something called Intent Classification, which tries to classify the text input as an intent and pairs it with a response that I have already set up previous. 

## Repository Structure
 - Everything associated with the bot itself is located in ./bot_model 
     - The data I'm using can be found in ./bot_model/data
        - answers.csv 
            - contains a list of my intents (int), intent_name(str), and response(str)
        - questions.csv
            - contains my training data, which are my questions and the intent (int) asscoiated with it. 
            - I created this dataset myself by looking through different interview prep sites. 

## Current Works
- Currently trying to set up a Websocket/Server 
    - I am somewhat satisifed with my model at the moment, but I need more datapoints to make sure. That's why I'm trying to create a way for people to interact with it. 
        - Want to create bot a Websocket & RESTful API 
            - Websocket
                - Users can interact with my bot
            - RESTful 
                - update my data so that I can have a list of misclassified questions and then train a new model. 