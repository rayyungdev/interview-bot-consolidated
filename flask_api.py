from flask import Flask, request
from threading import Thread
import sys
from flask_cors import CORS, cross_origin
from bot_model.mybot import *
from bot_model.utils import * 

raymond_bot = interview_bot()

app = Flask('__name__')
CORS(app, resources={r"/api/*": {"origins":"*"}})
app.config['CORS HEADERS'] = 'Content-Type'

@app.route('/')
@cross_origin()
def index():
    return str('Testing...')

@app.route('/user', methods = ['POST'])
@cross_origin()
def user():
    jsony = request.json
    data = jsony['msg']
    response = raymond_bot.respond(data)
    return response[0]

def run():
  CORS(app, resources={r"/api/*": {"origins":"*"}})
  app.run(host = '0.0.0.0', port=8080, ssl_context='adhoc')
  
def keep_alive():
  t = Thread(target = run())
  t.start()

if __name__ == '__main__':
  run()