import csv
import io
from datetime import date, timedelta, datetime
from collections import defaultdict

from flask import (Blueprint, render_template, redirect, url_for, flash,
                   request, Response)
from flask_login import (login_user, logout_user, login_required,
                         current_user)

from app import db
from app.models import User, Workout, Exercise, Meal, Measurement

# Tutte le route stanno in questo Blueprint chiamato 'main'.
main = Blueprint('main', __name__)


# ═════════════════════════════════════════════════════════════
# HOME PUBBLICA
# ═════════════════════════════════════════════════════════════
@main.route('/')
def index():
    """Landing page pubblica. Se sei loggato vai alla dashboard."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('index.html')


# ═════════════════════════════════════════════════════════════
# AUTENTICAZIONE (registrazione / login / logout)
# ═════════════════════════════════════════════════════════════
@main.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm_password', '')

        # Validazioni
        if not username or not email or not password:
            flash('Tutti i campi sono obbligatori.', 'danger')
            return render_template('register.html')
        if password != confirm:
            flash('Le due password non coincidono.', 'danger')
            return render_template('register.html')
        if len(password) < 6:
            flash('La password deve avere almeno 6 caratteri.', 'danger')
            return render_template('register.html')
        if User.query.filter_by(username=username).first():
            flash('Username già esistente.', 'danger')
            return render_template('register.html')
        if User.query.filter_by(email=email).first():
            flash('Email già registrata.', 'danger')
            return render_template('register.html')

        # Crea l'utente con password hashata
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash('Registrazione completata! Ora puoi accedere.', 'success')
        return redirect(url_for('main.login'))

    return render_template('register.html')


@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember') == 'on'

        user = User.query.filter_by(username=username).first()
        if user is None or not user.check_password(password):
            flash('Username o password errati.', 'danger')
            return render_template('login.html')

        login_user(user, remember=remember)
        flash(f'Bentornato, {user.username}!', 'success')
        next_page = request.args.get('next')
        return redirect(next_page or url_for('main.dashboard'))

    return render_template('login.html')


@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logout effettuato.', 'info')
    return redirect(url_for('main.index'))


# ═════════════════════════════════════════════════════════════
# DASHBOARD (riepilogo + grafici)
# ═════════════════════════════════════════════════════════════
@main.route('/dashboard')
@login_required
def dashboard():
    """Mostra statistiche e grafici dell'utente loggato."""
    oggi = date.today()
    sette_giorni_fa = oggi - timedelta(days=6)

    # --- Numeri riepilogativi (le "card" in alto) ---
    num_allenamenti = Workout.query.filter_by(user_id=current_user.id).count()
    num_pasti = Meal.query.filter_by(user_id=current_user.id).count()

    # Calorie di oggi (somma di tutti i pasti di oggi)
    pasti_oggi = Meal.query.filter_by(user_id=current_user.id,
                                      meal_date=oggi).all()
    calorie_oggi = sum(p.calories for p in pasti_oggi)
    proteine_oggi = sum(p.protein for p in pasti_oggi)
    carbo_oggi = sum(p.carbs for p in pasti_oggi)
    grassi_oggi = sum(p.fat for p in pasti_oggi)

    # Ultimo peso registrato
    ultima_misura = (Measurement.query
                     .filter_by(user_id=current_user.id)
                     .order_by(Measurement.measure_date.desc())
                     .first())
    ultimo_peso = ultima_misura.weight_kg if ultima_misura else None

    # --- GRAFICO 1: peso nel tempo (linea) ---
    misure = (Measurement.query
              .filter_by(user_id=current_user.id)
              .order_by(Measurement.measure_date.asc())
              .all())
    peso_labels = [m.measure_date.strftime('%d/%m') for m in misure]
    peso_valori = [m.weight_kg for m in misure]

    # --- GRAFICO 2: allenamenti negli ultimi 7 giorni (barre) ---
    # Prepara 7 giorni con conteggio 0, poi riempie
    giorni = [(sette_giorni_fa + timedelta(days=i)) for i in range(7)]
    conteggio_per_giorno = {g: 0 for g in giorni}
    allenamenti_settimana = (Workout.query
                             .filter(Workout.user_id == current_user.id,
                                     Workout.workout_date >= sette_giorni_fa)
                             .all())
    for w in allenamenti_settimana:
        if w.workout_date in conteggio_per_giorno:
            conteggio_per_giorno[w.workout_date] += 1
    allenamenti_labels = [g.strftime('%a %d/%m') for g in giorni]
    allenamenti_valori = [conteggio_per_giorno[g] for g in giorni]

    # --- GRAFICO 3: calorie ultimi 7 giorni (barre) ---
    calorie_per_giorno = {g: 0 for g in giorni}
    pasti_settimana = (Meal.query
                       .filter(Meal.user_id == current_user.id,
                               Meal.meal_date >= sette_giorni_fa)
                       .all())
    for p in pasti_settimana:
        if p.meal_date in calorie_per_giorno:
            calorie_per_giorno[p.meal_date] += p.calories
    calorie_labels = [g.strftime('%a %d/%m') for g in giorni]
    calorie_valori = [calorie_per_giorno[g] for g in giorni]

    return render_template(
        'dashboard.html',
        num_allenamenti=num_allenamenti,
        num_pasti=num_pasti,
        calorie_oggi=calorie_oggi,
        proteine_oggi=round(proteine_oggi, 1),
        carbo_oggi=round(carbo_oggi, 1),
        grassi_oggi=round(grassi_oggi, 1),
        ultimo_peso=ultimo_peso,
        peso_labels=peso_labels, peso_valori=peso_valori,
        allenamenti_labels=allenamenti_labels, allenamenti_valori=allenamenti_valori,
        calorie_labels=calorie_labels, calorie_valori=calorie_valori,
    )


# ═════════════════════════════════════════════════════════════
# ALLENAMENTI
# ═════════════════════════════════════════════════════════════
@main.route('/workouts')
@login_required
def workouts():
    """Lista di tutti gli allenamenti dell'utente, dal più recente."""
    lista = (Workout.query
             .filter_by(user_id=current_user.id)
             .order_by(Workout.workout_date.desc())
             .all())
    return render_template('workouts.html', workouts=lista)


@main.route('/workouts/new', methods=['GET', 'POST'])
@login_required
def create_workout():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        data_str = request.form.get('workout_date', '')
        notes = request.form.get('notes', '').strip()

        if not name:
            flash('Il nome dell\'allenamento è obbligatorio.', 'danger')
            return render_template('create_workout.html', oggi=date.today().isoformat())

        # Converte la stringa data del form in oggetto date
        try:
            w_date = datetime.strptime(data_str, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            w_date = date.today()

        workout = Workout(name=name, workout_date=w_date, notes=notes,
                          user=current_user)
        db.session.add(workout)
        db.session.commit()
        flash('Allenamento creato! Ora aggiungi gli esercizi.', 'success')
        return redirect(url_for('main.workout_detail', workout_id=workout.id))

    return render_template('create_workout.html', oggi=date.today().isoformat())


@main.route('/workouts/<int:workout_id>')
@login_required
def workout_detail(workout_id):
    workout = db.get_or_404(Workout, workout_id)
    # Sicurezza: l'utente può vedere solo i propri allenamenti
    if workout.user_id != current_user.id:
        flash('Non hai accesso a questo allenamento.', 'danger')
        return redirect(url_for('main.workouts'))
    return render_template('workout_detail.html', workout=workout)


@main.route('/workouts/<int:workout_id>/delete', methods=['POST'])
@login_required
def delete_workout(workout_id):
    workout = db.get_or_404(Workout, workout_id)
    if workout.user_id != current_user.id:
        flash('Operazione non permessa.', 'danger')
        return redirect(url_for('main.workouts'))
    db.session.delete(workout)
    db.session.commit()
    flash('Allenamento eliminato.', 'info')
    return redirect(url_for('main.workouts'))


@main.route('/workouts/<int:workout_id>/exercises/new', methods=['POST'])
@login_required
def add_exercise(workout_id):
    """Aggiunge un esercizio a un allenamento."""
    workout = db.get_or_404(Workout, workout_id)
    if workout.user_id != current_user.id:
        flash('Operazione non permessa.', 'danger')
        return redirect(url_for('main.workouts'))

    name = request.form.get('name', '').strip()
    if not name:
        flash('Il nome dell\'esercizio è obbligatorio.', 'danger')
        return redirect(url_for('main.workout_detail', workout_id=workout_id))

    # I campi numerici: se vuoti o errati, usa un default
    def to_int(value, default):
        try:
            return int(value)
        except (ValueError, TypeError):
            return default

    def to_float(value, default):
        try:
            return float(value)
        except (ValueError, TypeError):
            return default

    exercise = Exercise(
        name=name,
        sets=to_int(request.form.get('sets'), 3),
        reps=to_int(request.form.get('reps'), 10),
        weight=to_float(request.form.get('weight'), 0.0),
        workout=workout,
    )
    db.session.add(exercise)
    db.session.commit()
    flash(f'Esercizio "{name}" aggiunto.', 'success')
    return redirect(url_for('main.workout_detail', workout_id=workout_id))


@main.route('/exercises/<int:exercise_id>/delete', methods=['POST'])
@login_required
def delete_exercise(exercise_id):
    exercise = db.get_or_404(Exercise, exercise_id)
    workout_id = exercise.workout_id
    # Controlla che l'esercizio appartenga a un allenamento dell'utente
    if exercise.workout.user_id != current_user.id:
        flash('Operazione non permessa.', 'danger')
        return redirect(url_for('main.workouts'))
    db.session.delete(exercise)
    db.session.commit()
    flash('Esercizio eliminato.', 'info')
    return redirect(url_for('main.workout_detail', workout_id=workout_id))


# ═════════════════════════════════════════════════════════════
# ALIMENTAZIONE (diario pasti)
# ═════════════════════════════════════════════════════════════
@main.route('/nutrition')
@login_required
def nutrition():
    """Diario alimentare raggruppato per giorno."""
    pasti = (Meal.query
             .filter_by(user_id=current_user.id)
             .order_by(Meal.meal_date.desc(), Meal.created_at.asc())
             .all())

    # Raggruppa i pasti per data e calcola i totali del giorno
    giorni = defaultdict(list)
    for p in pasti:
        giorni[p.meal_date].append(p)

    # Ordina le date dalla più recente
    giorni_ordinati = []
    for d in sorted(giorni.keys(), reverse=True):
        lista_pasti = giorni[d]
        totali = {
            'calorie': sum(p.calories for p in lista_pasti),
            'proteine': round(sum(p.protein for p in lista_pasti), 1),
            'carbo': round(sum(p.carbs for p in lista_pasti), 1),
            'grassi': round(sum(p.fat for p in lista_pasti), 1),
        }
        giorni_ordinati.append((d, lista_pasti, totali))

    return render_template('nutrition.html', giorni=giorni_ordinati)


@main.route('/nutrition/new', methods=['GET', 'POST'])
@login_required
def create_meal():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        meal_type = request.form.get('meal_type', 'pranzo')
        data_str = request.form.get('meal_date', '')

        if not name:
            flash('Il nome del pasto è obbligatorio.', 'danger')
            return render_template('create_meal.html', oggi=date.today().isoformat())

        try:
            m_date = datetime.strptime(data_str, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            m_date = date.today()

        def to_int(value, default=0):
            try:
                return int(value)
            except (ValueError, TypeError):
                return default

        def to_float(value, default=0.0):
            try:
                return float(value)
            except (ValueError, TypeError):
                return default

        meal = Meal(
            name=name,
            meal_type=meal_type,
            meal_date=m_date,
            calories=to_int(request.form.get('calories')),
            protein=to_float(request.form.get('protein')),
            carbs=to_float(request.form.get('carbs')),
            fat=to_float(request.form.get('fat')),
            user=current_user,
        )
        db.session.add(meal)
        db.session.commit()
        flash('Pasto registrato!', 'success')
        return redirect(url_for('main.nutrition'))

    return render_template('create_meal.html', oggi=date.today().isoformat())


@main.route('/nutrition/<int:meal_id>/delete', methods=['POST'])
@login_required
def delete_meal(meal_id):
    meal = db.get_or_404(Meal, meal_id)
    if meal.user_id != current_user.id:
        flash('Operazione non permessa.', 'danger')
        return redirect(url_for('main.nutrition'))
    db.session.delete(meal)
    db.session.commit()
    flash('Pasto eliminato.', 'info')
    return redirect(url_for('main.nutrition'))


# ═════════════════════════════════════════════════════════════
# MISURAZIONI CORPOREE (peso)
# ═════════════════════════════════════════════════════════════
@main.route('/measurements')
@login_required
def measurements():
    lista = (Measurement.query
             .filter_by(user_id=current_user.id)
             .order_by(Measurement.measure_date.desc())
             .all())
    # Dati per il grafico (in ordine cronologico)
    cronologico = list(reversed(lista))
    labels = [m.measure_date.strftime('%d/%m/%Y') for m in cronologico]
    valori = [m.weight_kg for m in cronologico]
    return render_template('measurements.html', measurements=lista,
                           labels=labels, valori=valori,
                           oggi=date.today().isoformat())


@main.route('/measurements/new', methods=['POST'])
@login_required
def create_measurement():
    data_str = request.form.get('measure_date', '')
    peso_str = request.form.get('weight_kg', '')
    notes = request.form.get('notes', '').strip()

    try:
        peso = float(peso_str)
    except (ValueError, TypeError):
        flash('Inserisci un peso valido.', 'danger')
        return redirect(url_for('main.measurements'))

    try:
        m_date = datetime.strptime(data_str, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        m_date = date.today()

    m = Measurement(measure_date=m_date, weight_kg=peso, notes=notes,
                    user=current_user)
    db.session.add(m)
    db.session.commit()
    flash('Peso registrato!', 'success')
    return redirect(url_for('main.measurements'))


@main.route('/measurements/<int:measurement_id>/delete', methods=['POST'])
@login_required
def delete_measurement(measurement_id):
    m = db.get_or_404(Measurement, measurement_id)
    if m.user_id != current_user.id:
        flash('Operazione non permessa.', 'danger')
        return redirect(url_for('main.measurements'))
    db.session.delete(m)
    db.session.commit()
    flash('Misurazione eliminata.', 'info')
    return redirect(url_for('main.measurements'))


# ═════════════════════════════════════════════════════════════
# EXPORT DATI IN CSV
# ═════════════════════════════════════════════════════════════
@main.route('/export/workouts.csv')
@login_required
def export_workouts():
    """Genera e scarica un file CSV con tutti gli allenamenti ed esercizi."""
    output = io.StringIO()
    writer = csv.writer(output)
    # Intestazione
    writer.writerow(['Data', 'Allenamento', 'Esercizio', 'Serie',
                     'Ripetizioni', 'Peso (kg)', 'Volume'])

    lista = (Workout.query
             .filter_by(user_id=current_user.id)
             .order_by(Workout.workout_date.desc())
             .all())
    for w in lista:
        if w.exercises:
            for e in w.exercises:
                writer.writerow([w.workout_date, w.name, e.name,
                                 e.sets, e.reps, e.weight, e.volume])
        else:
            writer.writerow([w.workout_date, w.name, '(nessun esercizio)',
                             '', '', '', ''])

    # Restituisce il file come download
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=allenamenti.csv'}
    )