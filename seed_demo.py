"""
seed_demo.py — Popola il database con un utente demo e dati di esempio.

Esegui (dopo setup_db.py):  python seed_demo.py
Credenziali demo:  username = demo   password = demo1234

Utile per provare l'app senza inserire tutto a mano, e per la
presentazione al professore.
"""
from datetime import date, timedelta
from dotenv import load_dotenv
load_dotenv()

from app import create_app, db
from app.models import User, Workout, Exercise, Meal, Measurement

app = create_app()

with app.app_context():
    # Se l'utente demo esiste già, non duplicare
    if User.query.filter_by(username='demo').first():
        print("INFO: L'utente demo esiste gia'. Niente da fare.")
    else:
        demo = User(username='demo', email='demo@fitlog.it')
        demo.set_password('demo1234')
        db.session.add(demo)
        db.session.commit()

        oggi = date.today()

        # --- Allenamenti di esempio ---
        w1 = Workout(name='Petto e Tricipiti', workout_date=oggi - timedelta(days=2),
                     notes='Buona sessione, aumentato il peso sulla panca.', user=demo)
        w2 = Workout(name='Gambe', workout_date=oggi - timedelta(days=1), user=demo)
        db.session.add_all([w1, w2])
        db.session.commit()

        db.session.add_all([
            Exercise(name='Panca piana', sets=4, reps=8, weight=60, workout=w1),
            Exercise(name='Croci ai cavi', sets=3, reps=12, weight=15, workout=w1),
            Exercise(name='French press', sets=3, reps=10, weight=25, workout=w1),
            Exercise(name='Squat', sets=5, reps=5, weight=80, workout=w2),
            Exercise(name='Affondi', sets=3, reps=12, weight=20, workout=w2),
        ])

        # --- Pasti di esempio (oggi) ---
        db.session.add_all([
            Meal(name='Avena e banana', meal_type='colazione', meal_date=oggi,
                 calories=350, protein=12, carbs=60, fat=6, user=demo),
            Meal(name='Pollo, riso e verdure', meal_type='pranzo', meal_date=oggi,
                 calories=600, protein=45, carbs=70, fat=12, user=demo),
            Meal(name='Yogurt greco e mandorle', meal_type='spuntino', meal_date=oggi,
                 calories=220, protein=18, carbs=10, fat=11, user=demo),
        ])

        # --- Misurazioni di peso (ultime 4 settimane) ---
        pesi = [74.0, 73.5, 73.2, 72.8]
        for i, peso in enumerate(pesi):
            db.session.add(Measurement(
                measure_date=oggi - timedelta(days=(len(pesi) - 1 - i) * 7),
                weight_kg=peso, user=demo))

        db.session.commit()
        print("OK Dati demo creati!")
        print("   Login:  username = demo   password = demo1234")