from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

convention = {
  "ix": "ix_%(column_0_label)s",
  "uq": "uq_%(table_name)s_%(column_0_name)s",
  "ck": "ck_%(table_name)s_%(constraint_name)s",
  "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
  "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)
db = SQLAlchemy(metadata=metadata)

class Activity(db.Model, SerializerMixin):
    __tablename__ = 'activities'

    # serialize_rules=('-signups.activity', '-campers.activities', '-created_at', '-updated_at')
    serialize_only = ("id", "name", "difficulty",)

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    difficulty = db.Column(db.Integer)

    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())


    signups = db.relationship('Signup', back_populates="activity", cascade="all, delete-orphan")
    campers = association_proxy('signups', 'camper', creator=lambda camper_obj: Signup(camper=camper_obj))

    def __repr__(self):
        return f'<Activity {self.id}: {self.name}>'

class Camper(db.Model, SerializerMixin):
    __tablename__ = 'campers'

    # serialize_rules=('-signups.camper', '-activities.campers', '-created_at', '-updated_at')
    serialize_rules=('-signups.camper', '-created_at', '-updated_at')


    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    age = db.Column(db.Integer)

    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    signups = db.relationship('Signup', back_populates="camper", cascade="all, delete-orphan")
    activities = association_proxy('signups', 'activity', creator=lambda activity_obj: Signup(camper=activity_obj))

    def __repr__(self):
        return f'<Camper {self.id}: {self.name}>'

    @validates('name')
    def check_name(self, key, name):
        if name:
            return name
        raise ValueError('camper must have a name')

    @validates('age')
    def check_age(self, key, age):
        if 8 <= age <= 18:
            return age
        raise ValueError('camper must be between 8 and 18')

class Signup(db.Model, SerializerMixin):
    __tablename__ = 'signups'

    serialize_rules=('-activity.signups', '-camper.activities', '-created_at', '-updated_at')

    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.Integer)

    activity_id = db.Column(db.Integer, db.ForeignKey('activities.id'))
    camper_id = db.Column(db.Integer, db.ForeignKey('campers.id'))

    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    activity = db.relationship('Activity', back_populates="signups")
    camper = db.relationship('Camper', back_populates="signups")

    def __repr__(self):
        return f'<Signup {self.id}>'

    @validates('time')
    def check_time(self, key, time):
        if 0 <= time <= 23:
            return time
        raise ValueError('time must be between 0 and 23')

# add any models you may need.
