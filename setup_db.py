"""
setup_db.py — Crea tutte le tabelle del database.

Eseguito:
- In locale, una volta: python setup_db.py
- Su Render, come parte del Build Command.

db.create_all() crea le tabelle solo se non esistono già:
è sicuro eseguirlo più volte, non cancella i dati.
"""
from dotenv import load_dotenv
load_dotenv()

from app import create_app, db
# Importiamo i modelli così SQLAlchemy sa quali tabelle creare
from app.models import User, Workout, Exercise, Meal, Measurement

app = create_app()

with app.app_context():
    db.create_all()
    print("OK Database inizializzato!")
    print(f"   URI: {app.config['SQLALCHEMY_DATABASE_URI']}")