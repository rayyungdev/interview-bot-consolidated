from flask import Flask, jsonify, request
import flask
import flask_praetorian
from dotenv import load_dotenv
import os
import flask_cors 
import random
from bot_model.mybot import *
from bot_model.utils import *
from db.db_setup import *
from db.dynamo_setup import *

load_dotenv()
guard = flask_praetorian.Praetorian()
cors = flask_cors.CORS()
added_response = "\n\n*If you think my response was misclassified, use the command* `!misclassified` *to add your question to the database*"
instructions = "\n\nPlease help me to build my question dataset by using the command `!misclassified` when you think an answer is misclassified or if you think I should have answer to your question"

class hook_bot(interview_bot):
    def __init__(self):
        interview_bot.__init__(self)
        self.running_sessions = 0
        self.text_channel = dict()

    def retrieve_questions(self):
        return self.questions.to_dict()

    def initialize(self, id):
        self.running_sessions += 1
        print("Running Sessions : ", self.running_sessions)
        self.text_channel[id] = []

    def response_api(self, n, userID):
        response = self.predict(n)
        user_responses = get_answers(userID)
        del user_responses["ID"]
        return user_responses[response]

    def check_response(self, id, n, userID):
        if n.startswith('!'):
            command = n.split('!')[1]
            if command == 'misclassified':
                '''
                    Need to figure out how to access chat history...
                '''
                question_add(self.text_channel[id])
                return "Thank you! Your question has been added to the database"
            else:
                return 'Sorry, I don''t understand that command.\nIf you''re trying to label something as misclassiifed, use the command `!misclassified`'
        else:
            # self.text_channel.append(n)
            self.text_channel[id] = n
            response = self.response_api(n, userID)
            return response+added_response

    def retrieve_greeting(self, userID):
        user_responses = get_answers(userID)
        return {'message': user_responses["89"] + instructions, 'NAME' : user_responses["NAME"]}

    def delete_session(self, id):
        pass

raymond_bot = hook_bot()

app = Flask('__name__')
SECRET_KEY = os.getenv('SECRET_KEY')
# app.config['SECRET_KEY']= SECRET_KEY
app.config['SECRET_KEY'] = SECRET_KEY

app.config['JWT_ACCESS_LIFESPAN'] = {'hours': 24}
app.config['JWT_REFRESH_LIFESPAN'] = {'days': 30}

# Initialize the flask-praetorian instance for the app
guard.init_app(app, User)

# Initialize a local database for the example
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.getcwd(), 'database.db')}"
db.init_app(app)
cors.init_app(app)

with app.app_context():
    db.create_all()
    if db.session.query(User).filter_by(email='TESTING@interviewmeplz.com').count() < 1:
        db.session.add(User(
          email='TESTING@interviewmeplz.com',
          password=guard.hash_password('testies'),
          roles='test'
            ))
    db.session.commit()


# Set up some routes for the example
@app.route('/api/')
def home():
    return {"Hello": "World"}, 200

@app.route('/api/users', methods = ['POST'])
def new_user():
    req = flask.request.get_json(force=True)
    email = req.get('email', None)
    password = req.get('password', None)
    if email is None or password is None:
        return jsonify({"error" : "Missing Arguments"}), 400
        # abort(jsonify(error = "missing arguments")) # missing arguments
    if User.query.filter_by(email = email).first() is not None:
        return jsonify({"error" : "Email already exists..."}), 400

        # abort(jsonify(error = "email already exists")) # existing use
    password = guard.hash_password(password)
    user = User(email = email, password = password)

    db.session.add(user)
    db.session.commit()

    result = create_user({"ID" : user.id})
    if result == 200:
        return jsonify({ 'message': 'success!' }), 201
    else: 
        return jsonify({'message': 'something went wrong'}), 400
    ## Let's also create a section in the database for this user


@app.route('/api/login', methods=['POST'])
def login():
    """
    Logs a user in by parsing a POST request containing user credentials and
    issuing a JWT token.
    .. example::
       $ curl http://localhost:5000/api/login -X POST \
         -d '{"username":"Yasoob","password":"strongpassword"}'
    """
    req = request.get_json(force=True)
    email = req.get('email', None)
    password = req.get('password', None)
    user = guard.authenticate(email, password)
    ret = {'accessToken': guard.encode_jwt_token(user)}
    return jsonify(ret), 200
  
@app.route('/api/refresh', methods=['POST'])
def refresh():
    """
    Refreshes an existing JWT by creating a new one that is a copy of the old
    except that it has a refrehsed access expiration.
    .. example::
       $ curl http://localhost:5000/api/refresh -X GET \
         -H "Authorization: Bearer <your_token>"
    """
    print("refresh request")
    old_token = request.get_data()
    new_token = guard.refresh_jwt_token(old_token)
    ret = {'refreshToken': new_token}
    return jsonify(ret), 200
  
  
@app.route('/api/get_info')
@flask_praetorian.auth_required
def protected():
    """
    A protected endpoint. The auth_required decorator will require a header
    containing a valid JWT
    .. example::
       $ curl http://localhost:5000/api/protected -X GET \
         -H "Authorization: Bearer <your_token>"
    """
    user_id = flask_praetorian.current_user().id
    print(user_id)
    answers = True if len(get_answers(user_id)) > 1 else False
    if user_id is None: 
        return {'message': 'user not found'}, 404
    response = {
        'userID' : user_id,
        'hasResponses' : answers
    }
    return {'message': response}, 201 

@app.route('/api/retrieve_questions', methods = ['GET'])
@flask_praetorian.auth_required
def retrieve_questions():
    questions = raymond_bot.retrieve_questions()
    questions.update({"0" : "What would you like to name your bot?", 
    "999" : "Please set a default response for questions that we cannot necessarily interpret. "})
    answers = get_answers(flask_praetorian.current_user().id)
    if len(answers) > 1:
        answers["0"] = answers.pop("NAME")
    else: 
        answers = 0
        question_keys = list(questions.keys())
        answers = dict.fromkeys(question_keys, None)

    response = {
    'questions' : questions,
    "answers" : answers}
    return jsonify(response), 201

@app.route('/api/update_response', methods = ['POST'])
@flask_praetorian.auth_required
def update_response():
    answers = request.json
    answers["ID"] = flask_praetorian.current_user().id
    answers["NAME"] = answers.pop("0")
    try: 
        update_data(answers)
    except Exception as e:
        print("ERROR AT", e)
    finally: 
        response = {"message" : "Success!"}
        return jsonify(response), 201

@app.route('/api/greeting', methods = ['POST'])
def greeting():
    message = request.json
    if message["sessionID"] not in list(raymond_bot.text_channel.keys()):
        raymond_bot.initialize(message["sessionID"])
    intro = raymond_bot.retrieve_greeting(message["userID"])
    return jsonify(intro)

@app.route('/api/response', methods = ['POST'])
def response():
    message = request.json
    bot_response = raymond_bot.check_response(message["sessionID"], message['message'], message['userID'])
    return jsonify({"message": bot_response})

@app.route('/api/test')
def hello():
    msg = request.args.get("message")
    print(msg)
    return jsonify({"message":msg})

def run():
  app.run(host = '0.0.0.0', port=8080)


if __name__=="__main__":
    # ID = '51c1c976-a0bf-4a18-a042-fcac62cc46ca'
    # NAME = 'Raymond Bot'
    # testing_input = 'hello'
    # print(raymond_bot.response_api(testing_input, ID, NAME))

    # print(raymond_bot.retrieve_questions())
    run()
    