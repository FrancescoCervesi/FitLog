"""
run.py — Punto di ingresso dell'applicazione.

- In sviluppo:  python run.py
- In produzione: gunicorn run:app
                          ↑    ↑
                       file  variabile 'app'
"""
from dotenv import load_dotenv

# Carica le variabili dal file .env (deve avvenire PRIMA di create_app).
# In produzione su Render il file .env non esiste, ma load_dotenv()
# semplicemente non fa nulla — le variabili sono già nel sistema.
load_dotenv()

from app import create_app

app = create_app()

if __name__ == '__main__':
    # debug=True solo in locale: ricarica automatica + messaggi di errore.
    # MAI usare debug=True in produzione.
    app.run(debug=True)