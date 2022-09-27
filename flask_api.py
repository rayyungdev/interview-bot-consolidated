import os
import flask
import flask_sqlalchemy
import flask_praetorian
import flask_cors
from flask import request, jsonify, url_for

db = flask_sqlalchemy.SQLAlchemy()




# Initialize flask app for the example
app = flask.Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = 'top secret'
app.config['JWT_ACCESS_LIFESPAN'] = {'hours': 24}
app.config['JWT_REFRESH_LIFESPAN'] = {'days': 30}

# Initialize the flask-praetorian instance for the app
guard.init_app(app, User)

# Initialize a local database for the example
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.getcwd(), 'database.db')}"
db.init_app(app)

# Initializes CORS so that the api_tool can talk to the example app
cors.init_app(app)

# Add users for the example

with app.app_context():
    db.create_all()
    if db.session.query(User).filter_by(email='TESTacc@balls.com').count() < 1:
        db.session.add(User(
          email='TESTacc@balls.com',
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
    email = request.json.get('email')
    password = request.json.get('password')
    if email is None or password is None:
        abort(400) # missing arguments
    if User.query.filter_by(email = email).first() is not None:
        abort(400) # existing use
    password = guard.hash_password(password)
    user = User(email = email, password = password)

    db.session.add(user)
    db.session.commit()
    return jsonify({ 'email': user.email }), 201


@app.route('/api/login', methods=['POST'])
def login():
    """
    Logs a user in by parsing a POST request containing user credentials and
    issuing a JWT token.
    .. example::
       $ curl http://localhost:5000/api/login -X POST \
         -d '{"username":"Yasoob","password":"strongpassword"}'
    """
    req = flask.request.get_json(force=True)
    email = req.get('email', None)
    password = req.get('password', None)
    user = guard.authenticate(email, password)
    ret = {'access_token': guard.encode_jwt_token(user)}
    return ret, 200
  
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
    ret = {'access_token': new_token}
    return ret, 200
  
  
@app.route('/api/protected')
@flask_praetorian.auth_required
def protected():
    """
    A protected endpoint. The auth_required decorator will require a header
    containing a valid JWT
    .. example::
       $ curl http://localhost:5000/api/protected -X GET \
         -H "Authorization: Bearer <your_token>"
    """
    return {'message': f'protected endpoint (allowed user {flask_praetorian.current_user().email})'}


# Run the example
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)