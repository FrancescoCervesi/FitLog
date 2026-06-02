from datetime import datetime, date, timezone
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager


# Flask-Login chiama questa funzione per ricaricare l'utente
# a partire dall'id salvato nel cookie di sessione.
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


# ─────────────────────────────────────────────────────────────
# UTENTE
# ─────────────────────────────────────────────────────────────
class User(UserMixin, db.Model):
    """
    Modello Utente.
    UserMixin fornisce i metodi richiesti da Flask-Login
    (is_authenticated, get_id(), ecc.).
    """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relazioni: un utente ha molti allenamenti, pasti e misurazioni.
    # cascade='all, delete-orphan' => se cancello l'utente,
    # spariscono anche i suoi dati collegati.
    workouts = db.relationship('Workout', backref='user', lazy=True,
                               cascade='all, delete-orphan')
    meals = db.relationship('Meal', backref='user', lazy=True,
                            cascade='all, delete-orphan')
    measurements = db.relationship('Measurement', backref='user', lazy=True,
                                   cascade='all, delete-orphan')

    def set_password(self, password):
        """Salva l'HASH della password, mai la password in chiaro."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Confronta la password inserita con l'hash salvato."""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


# ─────────────────────────────────────────────────────────────
# ALLENAMENTO
# ─────────────────────────────────────────────────────────────
class Workout(db.Model):
    """Una sessione di allenamento (es. 'Petto e Tricipiti')."""
    __tablename__ = 'workouts'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    workout_date = db.Column(db.Date, nullable=False, default=date.today)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Un allenamento contiene molti esercizi
    exercises = db.relationship('Exercise', backref='workout', lazy=True,
                                cascade='all, delete-orphan')

    @property
    def total_volume(self):
        """Volume totale = somma di (serie x ripetizioni x peso) di ogni esercizio.
        È un indicatore del lavoro svolto nell'allenamento."""
        return sum(e.volume for e in self.exercises)

    def __repr__(self):
        return f'<Workout {self.name}>'


# ─────────────────────────────────────────────────────────────
# ESERCIZIO (dentro un allenamento)
# ─────────────────────────────────────────────────────────────
class Exercise(db.Model):
    """Un esercizio dentro un allenamento (es. 'Panca piana 4x8 @60kg')."""
    __tablename__ = 'exercises'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    sets = db.Column(db.Integer, nullable=False, default=3)       # serie
    reps = db.Column(db.Integer, nullable=False, default=10)      # ripetizioni
    weight = db.Column(db.Float, nullable=False, default=0.0)     # peso in kg

    workout_id = db.Column(db.Integer, db.ForeignKey('workouts.id'),
                           nullable=False)

    @property
    def volume(self):
        """Volume dell'esercizio = serie x ripetizioni x peso."""
        return self.sets * self.reps * self.weight

    def __repr__(self):
        return f'<Exercise {self.name}>'


# ─────────────────────────────────────────────────────────────
# PASTO (diario alimentare)
# ─────────────────────────────────────────────────────────────
class Meal(db.Model):
    """Un pasto registrato con calorie e macronutrienti."""
    __tablename__ = 'meals'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    # Tipo di pasto: colazione, pranzo, cena, spuntino
    meal_type = db.Column(db.String(30), nullable=False, default='pranzo')
    meal_date = db.Column(db.Date, nullable=False, default=date.today)

    calories = db.Column(db.Integer, nullable=False, default=0)   # kcal
    protein = db.Column(db.Float, nullable=False, default=0.0)    # proteine (g)
    carbs = db.Column(db.Float, nullable=False, default=0.0)      # carboidrati (g)
    fat = db.Column(db.Float, nullable=False, default=0.0)        # grassi (g)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def __repr__(self):
        return f'<Meal {self.name}>'


# ─────────────────────────────────────────────────────────────
# MISURAZIONE CORPOREA (peso nel tempo)
# ─────────────────────────────────────────────────────────────
class Measurement(db.Model):
    """Registra il peso corporeo in una certa data, per i grafici di progresso."""
    __tablename__ = 'measurements'

    id = db.Column(db.Integer, primary_key=True)
    measure_date = db.Column(db.Date, nullable=False, default=date.today)
    weight_kg = db.Column(db.Float, nullable=False)
    notes = db.Column(db.String(200), nullable=True)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def __repr__(self):
        return f'<Measurement {self.weight_kg}kg il {self.measure_date}>'