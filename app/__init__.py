import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# ─────────────────────────────────────────────────────────────
# Oggetti globali creati FUORI dalla factory, così possono essere
# importati dagli altri file (models.py, routes.py).
# Vengono "collegati" all'app dentro create_app() con .init_app()
# ─────────────────────────────────────────────────────────────
db = SQLAlchemy()
login_manager = LoginManager()


def create_app():
    """
    Application Factory: funzione che crea e configura l'app Flask.
    Questo pattern permette di tenere la configurazione ordinata e
    di creare più istanze dell'app (utile per i test).
    """
    app = Flask(__name__,
                instance_relative_config=True,
                template_folder='../templates',
                static_folder='static')

    # ── CONFIGURAZIONE ──────────────────────────────────────
    app.config.from_mapping(
        # SECRET_KEY: serve a Flask per firmare i cookie di sessione.
        # Viene letta dalle variabili d'ambiente (.env in locale,
        # pannello Render in produzione). MAI scriverla nel codice!
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev-cambiami-in-produzione'),

        # Database: in locale SQLite (file), in produzione PostgreSQL
        SQLALCHEMY_DATABASE_URI=os.environ.get(
            'DATABASE_URL',
            'sqlite:///' + os.path.join(app.instance_path, 'fitlog.sqlite')
        ),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    # Render a volte fornisce URL che iniziano con "postgres://",
    # ma SQLAlchemy moderno richiede "postgresql://". Questo fix lo corregge.
    uri = app.config['SQLALCHEMY_DATABASE_URI']
    if uri.startswith("postgres://"):
        app.config['SQLALCHEMY_DATABASE_URI'] = uri.replace(
            "postgres://", "postgresql://", 1)

    # Crea la cartella 'instance' (dove vive il file SQLite) se non esiste
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # ── INIZIALIZZAZIONE ESTENSIONI ─────────────────────────
    db.init_app(app)
    login_manager.init_app(app)
    # Se un utente non loggato apre una pagina protetta, viene mandato qui:
    login_manager.login_view = 'main.login'
    login_manager.login_message = 'Devi accedere per vedere questa pagina.'
    login_manager.login_message_category = 'warning'

    # ── REGISTRAZIONE DELLE ROUTE (Blueprint) ───────────────
    from app.routes import main
    app.register_blueprint(main)

    return app