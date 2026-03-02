from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, ValidationError, EqualTo, Email, Length
from .models import *


class LoginForm(FlaskForm):
    username = StringField('Usuario', validators=[DataRequired()])
    password = PasswordField('Senha', validators=[DataRequired()])
    remember_me = BooleanField("Lembrar-me")
    submit = SubmitField('Entrar')

class RegistrationForm(FlaskForm):
    username = StringField('Usuário', validators=[DataRequired(), Length(min=3)])
    password = PasswordField('Senha', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('Repita a senha', validators=[DataRequired(), EqualTo('password'), Length(min=6)])
    submit = SubmitField('Registrar')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Por favor, use um nome de usuário diferente.')
        
class BookForm(FlaskForm):
    title = StringField('Título', validators=[DataRequired()])
    author = StringField('Autor', validators=[DataRequired()])
    type = SelectField ('Gênero', 
                            coerce=int,
                            validators=[DataRequired()])
    available = BooleanField('Disponível')
    submit = SubmitField('Salvar')


class PersonForm(FlaskForm):
    nome = StringField('nome', validators=[DataRequired()])
    sobrenome = StringField('sobrnome', validators=[DataRequired()])
    email = StringField('email', validators=[DataRequired(), Email()])
    submit = SubmitField('Salvar')

    def __init__(self, person_id=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.person_id = person_id

    def validate_email(self, email):
        existing_email = Person.query.filter_by(email=email.data).first()
        if existing_email and existing_email.id != self.person_id:
            raise ValidationError('Por favor, cadastre um nome de E-mail diferente.')
        
    

class BorrowForm(FlaskForm):
    book_id = SelectField('Livro', coerce=int, validators=[DataRequired()])
    person_id = SelectField('Pessoa', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Emprestar')
