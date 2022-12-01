import flask_sqlalchemy
import uuid

# A generic user model that might be used by an app powered by flask-praetorian
db = flask_sqlalchemy.SQLAlchemy()

class User(db.Model):
    id = db.Column('id', db.Text(length=36), default=lambda: str(uuid.uuid4()), primary_key=True)
    email = db.Column(db.Text, unique=True)
    password = db.Column(db.Text)
    roles = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True, server_default='true')

    @property
    def rolenames(self):
        try:
            return self.roles.split(',')
        except Exception:
            return []

    @classmethod
    def lookup(cls, email):
        return cls.query.filter_by(email=email).one_or_none()

    @classmethod
    def identify(cls, id):
        return cls.query.get(id)

    @property
    def identity(self):
        return self.id

    def is_valid(self):
        return self.is_active

# class Answers(db.Model):
#     id = db.Column(db.Integer, primary_key = True)
#     content = db.Column(db.Text)
#     userID = db.Column(db.Integer, db.ForeignKey('user.id'))

#     def __repr__(self):
#             return f'<ID "{self.content}">'