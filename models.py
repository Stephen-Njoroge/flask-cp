from flask_sqlalchemy import SQLAlchemy
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from marshmallow import Schema, fields, ValidationError
from passlib.apps import custom_app_context as pwd_context

db = SQLAlchemy()


class User(db.Model):
    '''
    Create a table for the users.
    '''
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), index=True)
    password_hash = db.Column(db.String(64))  # To store hashed passwords.

    def hash_password(self, password):
        ''' Method to encrypt password'''
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        '''To verify a password'''
        return pwd_context.verify(password, self.password_hash)

    def generate_auth_token(self, SECRET_KEY, expiration=600):
        s = Serializer(SECRET_KEY, expires_in=expiration)
        return s.dumps({'id': self.id})


class Bucketlist(db.Model):
    '''Method to create tables for the bucketlists'''
    __tablename__ = 'bucketlists'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=False)
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(db.DateTime, default=db.func.current_timestamp())
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    created_by = db.relationship(
        "User", backref=db.backref("users.username", lazy="dynamic"))
    items = db.relationship("Item", backref=db.backref("bucketlists"))

    def __repr__(self):
        return "<Bucketlist(created_by='%s')>" % (
            self.created_by)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Item(db.Model):
    '''Method to create tables for the items'''
    __tablename__ = 'items'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=False)
    bucketlist_id = db.Column(db.Integer, db.ForeignKey('bucketlists.id'))
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(db.DateTime, default=db.func.current_timestamp())
    done = db.Column(db.Boolean, default=False)


class UserSchema(Schema):
    '''UserSchema for data serialization using marshmallow'''
    id = fields.Int(dump_only=True)
    username = fields.Str()


def must_not_be_blank(data):
    if not data:
        raise ValidationError('Data not provided.')


class ItemSchema(Schema):
    '''ItemSchema for data serialization using marshmallow'''
    id = fields.Int(dump_only=True)
    name = fields.Str()
    date_created = fields.DateTime(dump_only=True)
    date_modified = fields.DateTime(dump_only=True)
    done = fields.Boolean()


class BucketlistSchema(Schema):
    '''BucketlistSchema for data serialization using marshmallow'''
    id = fields.Int(dump_only=True)
    name = fields.Str()
    date_created = fields.DateTime(dump_only=True)
    date_modified = fields.DateTime(dump_only=True)
    created_by = fields.Nested(UserSchema, only=('username'))
    items = fields.Nested(ItemSchema, many=True)


user_schema = UserSchema()
users_schema = UserSchema(many=True)
bucketlist_schema = BucketlistSchema()
bucketlists_schema = BucketlistSchema(many=True)
item_schema = ItemSchema()
items_schema = ItemSchema(many=True)
