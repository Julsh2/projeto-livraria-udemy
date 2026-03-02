from app import create_app
from app.models import Type
from app.extensions import db


app = create_app()

def seed_types():
    types = [
            "Romance",
            "Fantasia",
            "Drama",
            "Biografia",
            "Terror",
            'Ficção']
    
    for t in types:
        if not Type.query.filter_by(name=t).first():
            db.session.add(Type(name=t))

    db.session.commit()

with app.app_context():
    seed_types()

print("Seeds criados!")