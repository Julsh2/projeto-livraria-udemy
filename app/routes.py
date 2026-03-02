import json
from flask import redirect, url_for, render_template, request, flash, jsonify
from flask_login import login_user, logout_user, current_user, login_required
from app import db
from .models import *
from .forms import *
from flask import current_app as app
from datetime import datetime


@app.route('/')
@login_required
def index():

    # Função da rota principal (provavelmente renderiza a página inicial)
    
    ranking_person = (
        db.session.query(
            Person.nome,              # Pega o nome da pessoa para mostrar no ranking
            db.func.count(Borrow.id)  # Conta quantos empréstimos cada pessoa fez
                                      # COUNT() conta quantas vezes aparece um empréstimo
        )

        .join(Borrow)                 # Junta a tabela Person com a tabela Borrow
                                      # Isso permite saber quais empréstimos pertencem a cada pessoa
                                      # Funciona porque existe relacionamento entre as tabelas

        .group_by(Person.id)          # Agrupa os resultados por pessoa
                                      # Necessário porque estamos usando COUNT()
                                      # Senão o banco não sabe como separar as contagens por pessoa

        .order_by(                    # Ordena o resultado
            db.func.count(Borrow.id).desc()   # Ordena do maior número de empréstimos
                                             # para o menor (ranking decrescente)
        )

        .all()                        # Executa a query e retorna todos os resultados
                                      # Sem o .all(), a query só estaria sendo montada
    )
    

    ranking_books = db.session.query(Book.title, db.func.count(Borrow.id)).join(Borrow).group_by(Book.id).order_by(db.func.count(Borrow.id).desc()).all()
    book_type = db.session.query(Type.name, db.func.count(Book.id)).join(Book).group_by(Type.name).all()
    available_books = db.session.query(Book).filter_by(available = True).count()
    unavailable_books = db.session.query(Book).filter_by(available = False).count()


# Usando person[0] porque cada item da lista é uma tupla (nome, quantidade), e [0] pega o nome da pessoa
    ranking_persons_data = {
        'labels': [person[0] for person in ranking_person],
        'data': [person[1] for person in ranking_person],
            }

    ranking_books_data = {
        'labels': [books[0] for books in ranking_books],
        'data': [books[1] for books in ranking_books],
            }
    

# Aqui separo "tipo do livro" e "quantidade" direto porque a query retorna algo como:
# ("Fantasia", 10)
# ("Romance", 5)
#
# Então:
# tipo → vai para os labels (nomes)
# quantidade → vai para os dados do gráfico

    book_type_data = {
        'labels': [tipo for tipo, qnt in book_type],
        'data': [qnt for tipo, qnt in book_type],
            }
    


    return render_template("index.html",
            ranking_books_data = json.dumps(ranking_books_data),
            ranking_persons_data = json.dumps(ranking_persons_data),
            book_type_data = json.dumps(book_type_data),
            available_books = available_books,
            unavailable_books = unavailable_books)


@app.route('/login', methods=['GET', 'POST'])
def login():

    if current_user.is_authenticated: #se o rapaz já está logado
        return redirect(url_for("index"))
    

    form = LoginForm()

    if form.validate_on_submit(): #passou na validação de email senha string email?
        print ("Formulário válido")
        user = User.query.filter_by(username=form.username.data).first() #buscou se tem no db
       
       
        if user is None or not user.check_password(form.password.data): #se nao for, retorna incorreto
            print ("user inválido")
            flash("Nome de usuário ou senha incorreto")
            return redirect(url_for('login'))
        
        login_user(user, remember=form.remember_me.data)
        print("login efetuado")
        user.last_login = datetime.utcnow()
        db.session.commit()
        return redirect(url_for('index'))

    return render_template(
        "login.html",
        form = form
    )

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():

    if current_user.is_authenticated:
        return redirect(url_for("index"))

    form = RegistrationForm()

    if form.validate_on_submit():
        print("passou da validação")
        user = User (
            username = form.username.data
        )
        flash("Parabéns, você concluiu seu cadastro!")

    
        user.set_password(form.password.data)
    
        print("Parabéns, você concluiu seu cadastro!")

        db.session.add(user)
        db.session.commit() 
        return redirect(url_for("login"))

    return render_template(
        'register.html',
        form = form
    )


@app.route('/books', methods = ['GET', 'POST'])
@login_required
def manage_books():
    form = BookForm()
     # popula dropdown
    form.type.choices = [
        (t.id, t.name) for t in Type.query.all()
    ]

    if form.validate_on_submit():
        book = Book(
            title = form.title.data,
            author = form.author.data,
            type_id = form.type.data,
            available = form.available.data,
            created_by = current_user.id,
            updated_by = current_user.id,
        )

        db.session.add(book)
        db.session.commit()

        return redirect(url_for('manage_books'))
    
    books = Book.query.all() # select * from book
    return render_template(
        'books.html',
        form = form,
        books = books
    )

@app.route('/people', methods=['GET', 'POST'])
@login_required
def manage_people():
    form = PersonForm()

    if form.validate_on_submit():
        person = Person(
            nome = form.nome.data,
            sobrenome = form.sobrenome.data,
            email = form.email.data,
            updated_by = current_user.id,
            created_by = current_user.id
        )
        db.session.add(person)
        db.session.commit()

        return redirect(url_for('manage_people'))
    
    person = Person.query.all()
    return render_template(
        'people.html',
        form = form,
        people = person
    )

@app.route('/people/delete/<int:person_id>', methods = ['GET', 'POST'])
def delete_people(person_id):
    person = Person.query.get_or_404(person_id)

    db.session.delete(person)
    db.session.commit()

    return redirect(url_for('manage_people'))


@app.route('/books/delete/<int:book_id>', methods=['GET', 'POST'])
@login_required
def delete_book(book_id):
   book = Book.query.get_or_404(book_id) #verifica se tem essa id

   #remover todas as referências nas outras tabelas

   Borrow.query.filter_by(book_id = book_id).delete()
   Historical.query.filter_by(book_id = book_id).delete()

   db.session.delete(book)
   db.session.commit()

   return redirect(url_for('manage_books'))


@app.route('/books/update/<int:book_id>', methods=['GET','POST'])
@login_required
def update_book(book_id):
    book = Book.query.get_or_404(book_id)
    form = BookForm(obj=book)

    form.type.choices = [
    (t.id, t.name) for t in Type.query.all()
    ]


    if form.validate_on_submit():
        book.title = form.title.data
        book.author = form.author.data
        book.type_id = form.type.data  
        book.available = form.available.data
        book.updated_by = current_user.id
        db.session.commit()

        return redirect(url_for("manage_books"))
    
    return render_template(
        "book_form.html",
        form=form
    )

@app.route('/people/update/<int:person_id>', methods = ['GET', 'POST'])
@login_required
def update_people(person_id):

    #obj=person. Serve para preencher automaticamente o formulário com os dados atuais da pessoa.
    #person_id=person.id. Formulário, guarde o ID da pessoa que estou editando.
    person = Person.query.get_or_404(person_id)
    form = PersonForm(person_id=person.id, obj=person)

    if form.validate_on_submit():
        print("VALIDOU")
        person.nome = form.nome.data
        person.sobrenome = form.sobrenome.data
        person.email = form.email.data
        person.updated_by = current_user.id
        db.session.commit()

        return redirect(url_for('manage_people'))
    
    return render_template(
        'person_form.html',
        form=form
    )


@app.route('/borrow', methods=['GET', 'POST'])
@login_required
def borrow_book():
    
    form = BorrowForm()

    form.book_id.choices = [(book.id, book.title) for book in Book.query.filter_by(available=True).all()]
    form.person_id.choices = [(person.id, f"{person.nome} {person.sobrenome}") for person in Person.query.all()]

    if form.validate_on_submit():
        borrow = Borrow(
            book_id = form.book_id.data,
            person_id = form.person_id.data,
            created_by = current_user.id,
            updated_by = current_user.id
        )


        book = Book.query.get(form.book_id.data) #Pegue o livro que foi escolhido e marque como indisponível
        book.available = False

        db.session.add(borrow)
        db.session.commit()


        historico = Historical(
            book_id = form.book_id.data,
            person_id = form.person_id.data,
            borrow_date = datetime.utcnow()
        )

        db.session.add(historico)
        db.session.commit()
        return redirect(url_for('borrow_book'))

    return render_template (
        "borrow_form.html",
        form=form
    )

@app.route('/historical', methods = ['GET', 'POST'])
@login_required
def view_historical():
    historical = Historical.query.order_by(Historical.borrow_date.desc())

    return render_template(
    "historico.html",
    historical = historical 
    )