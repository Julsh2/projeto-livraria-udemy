from datetime import datetime, timedelta
from .extensions import db, csrf, login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(150), unique = True, nullable = False)
    password_hash = db.Column(db.String(128), nullable = False)
    last_login = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow) 
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_books = db.relationship('Book', foreign_keys ='Book.created_by', backref='creator', lazy=True)
    updated_books = db.relationship('Book', foreign_keys = 'Book.updated_by', backref='updater', lazy =True)

#cria a senha do usuário
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

#checa a senha do usuário existente
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
class Book(db.Model):
    __tablename__ = "book"
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(150), nullable = False)
    author = db.Column(db.String(120), nullable = False)
    type_id = db.Column(db.Integer, db.ForeignKey('type.id'), nullable = False)
    type = db.relationship('Type', backref='books')
    available = db.Column(db.Boolean, default = True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow) 
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    updated_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    borrows = db.relationship('Borrow', backref='book', lazy=True, cascade="all, delete-orphan")
    historical = db.relationship('Historical', backref='book', lazy=True, cascade="all, delete-orphan")

class Person(db.Model):
    __tablename__ = "person"
    id = db.Column(db.Integer, primary_key = True)
    nome = db.Column(db.String(100), nullable = False)
    sobrenome = db.Column(db.String(100), nullable = False)
    email = db.Column(db.String(150), unique = True, nullable = False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow) 
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    updated_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    borrows = db.relationship('Borrow', backref='person', lazy=True, cascade="all, delete-orphan")
    historical = db.relationship('Historical', backref='person', lazy=True, cascade="all, delete-orphan")

class Borrow(db.Model):
    __tablename__ = "borrow"
    id = db.Column(db.Integer, primary_key = True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable = False)
    person_id = db.Column(db.Integer, db.ForeignKey('person.id'), nullable = False)
    borrow_date = db.Column (db.DateTime, default=datetime.utcnow)

    return_date = db.Column (db.DateTime, default=lambda: datetime.utcnow() + timedelta(days=7))

    created_at = db.Column(db.DateTime, default=datetime.utcnow) 
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    updated_by = db.Column(db.Integer, db.ForeignKey('user.id'))

class Historical(db.Model):
    __tablename__ = 'historical'
    id = db.Column(db.Integer, primary_key = True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id', name='fk_historical_book_id'), nullable = False)
    person_id = db.Column(db.Integer, db.ForeignKey('person.id', name='fk_historical_person_id'), nullable = False)
    borrow_date = db.Column (db.DateTime, nullable=False)
    return_date = db.Column (db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow) 


class Type(db.Model):
    __tablename__ = 'type'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(100), unique = True, nullable = False)


def type_query():
    return Type.query