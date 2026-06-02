# FitLog 💪

Applicazione web per la gestione degli allenamenti e dell'alimentazione, sviluppata con Python e Flask.

> 🚀 **Link all'applicazione live:** _(da inserire dopo il deploy, es. https://fitlog.onrender.com)_
> Autore: **Francesco Cervesi** | Classe 5ª | A.S. 2025/2026

---

## Indice

1. [Funzionalità](#funzionalità)
2. [Installazione e avvio](#installazione-e-avvio)
3. [Come usare l'applicazione](#come-usare-lapplicazione)
4. [Deploy su Render](#deploy-su-render)
5. [Tecnologie usate](#tecnologie-usate)

---

## Funzionalità

- **Autenticazione utenti** — registrazione, login, logout con password cifrata (hash).
- **Allenamenti** — creazione di sessioni di allenamento con esercizi (serie, ripetizioni, peso) e calcolo automatico del volume di lavoro.
- **Diario alimentare** — registrazione dei pasti con calorie e macronutrienti (proteine, carboidrati, grassi), raggruppati per giorno con totali.
- **Peso corporeo** — registrazione del peso nel tempo con grafico di andamento.
- **Dashboard** — riepilogo con grafici interattivi: peso, calorie giornaliere, frequenza degli allenamenti, ripartizione dei macronutrienti.
- **Export CSV** — esportazione di tutti gli allenamenti in un file scaricabile.
- Ogni utente vede e modifica **solo i propri dati**.

---

## Installazione e avvio

**Prerequisiti:** Python 3.10 o superiore, pip.

```bash
# 1. Clona il repository
git clone https://github.com/TUO-USERNAME/FitLog.git
cd FitLog

# 2. (Opzionale ma consigliato) crea e attiva l'ambiente virtuale
python -m venv venv
venv\Scripts\activate           # Windows
# source venv/bin/activate      # Mac/Linux

# 3. Installa le dipendenze
pip install -r requirements.txt

# 4. Crea il file delle credenziali
copy .env.example .env          # Windows
# cp .env.example .env          # Mac/Linux
# Poi apri .env e inserisci una SECRET_KEY a tua scelta

# 5. Inizializza il database
python setup_db.py

# 6. (Opzionale) Popola con un account e dati demo
python seed_demo.py
# Login demo:  username = demo   password = demo1234

# 7. Avvia l'applicazione
python run.py
```

L'app sarà disponibile su `http://127.0.0.1:5000`.

---

## Come usare l'applicazione

### Registrazione e login
1. Apri `http://127.0.0.1:5000`
2. Clicca **Registrati** e inserisci username, email e password
3. Effettua il **Login** con le credenziali create

### Dashboard
Dopo il login vieni reindirizzato alla **dashboard**, che mostra le statistiche principali e quattro grafici: andamento del peso, macronutrienti di oggi, allenamenti e calorie degli ultimi 7 giorni.

### Allenamenti
- **Crea allenamento**: dal menu **Allenamenti** → **+ Nuovo allenamento**, inserisci nome, data ed eventuali note.
- **Aggiungi esercizi**: nella pagina di dettaglio dell'allenamento, compila il form in fondo con nome, serie, ripetizioni e peso.
- **Elimina** esercizi o l'intero allenamento con i pulsanti dedicati.
- **Esporta** tutti gli allenamenti in CSV con il pulsante **Esporta CSV**.

### Alimentazione
- Dal menu **Alimentazione** → **+ Registra pasto**, inserisci nome, tipo (colazione/pranzo/cena/spuntino), data, calorie e macronutrienti.
- I pasti sono raggruppati per giorno, con i totali giornalieri in alto.

### Peso
- Dal menu **Peso**, registra il tuo peso corporeo. Il grafico si aggiorna automaticamente mostrando l'andamento nel tempo.

### Logout
- Clicca **Logout** in alto a destra per uscire.

---

## Deploy su Render

1. Crea un account su [render.com](https://render.com)
2. Clicca **New → Web Service** e collega il repository GitHub
3. Render rileva automaticamente la configurazione dal file `render.yaml`
4. La variabile `SECRET_KEY` viene generata automaticamente
5. Clicca **Deploy** — al primo avvio il database viene creato dal Build Command

> **Nota:** il piano gratuito di Render spegne il servizio dopo 15 minuti di inattività e usa un disco "effimero": i dati salvati in SQLite si azzerano a ogni riavvio. Per renderli permanenti si collega un database **PostgreSQL** (vedi REPORT.md).

---

## Tecnologie usate

| Componente | Tecnologia |
|------------|-----------|
| Linguaggio | Python 3 |
| Framework web | Flask |
| Database (ORM) | SQLAlchemy + SQLite / PostgreSQL |
| Autenticazione | Flask-Login |
| Server di produzione | Gunicorn |
| Frontend | HTML, Jinja2, Bootstrap 5 |
| Grafici | Chart.js |
| Hosting | Render.com |

---

## Licenza

Progetto realizzato a scopo didattico — Maturità A.S. 2025/2026.