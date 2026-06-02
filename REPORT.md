# Relazione Tecnica — FitLog

**Autore:** Francesco Cervesi · **Classe:** 5ª · **A.S.** 2025/2026

---

## 1. Introduzione

FitLog è un'applicazione web per la gestione delle attività di allenamento e dell'alimentazione. L'obiettivo del progetto è permettere a un utente di registrare i propri allenamenti (con i relativi esercizi), tenere un diario alimentare con il conteggio di calorie e macronutrienti, monitorare il peso corporeo nel tempo e visualizzare i propri progressi tramite grafici.

Il progetto nasce come esercitazione completa che copre l'intero ciclo di sviluppo di un'applicazione web: progettazione del database, sviluppo del back-end, realizzazione dell'interfaccia, gestione dell'autenticazione e infine deployment in produzione su una piattaforma cloud.

---

## 2. Architettura dell'applicazione

L'applicazione segue il pattern **MVC** (Model-View-Controller), tipico delle applicazioni Flask strutturate:

- **Model** (`app/models.py`): definisce le tabelle del database tramite classi Python (ORM SQLAlchemy).
- **View** (`app/templates/`): i file HTML con il motore di template Jinja2, che generano le pagine mostrate all'utente.
- **Controller** (`app/routes.py`): le funzioni associate agli URL, che ricevono le richieste, interagiscono con il database e restituiscono le pagine.

L'app è organizzata con il pattern **Application Factory** (`create_app()` in `app/__init__.py`), che separa la configurazione dalla creazione dell'app e facilita i test e il deploy.

Le route sono raggruppate in un **Blueprint** chiamato `main`, una funzionalità di Flask che permette di organizzare in modo modulare le diverse parti dell'applicazione.

### Schema dell'architettura

```
                    ┌─────────────────┐
   Browser  ───────▶│   Gunicorn      │  (server WSGI di produzione)
   (utente)         │   + Flask app   │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
         routes.py       templates/      models.py
        (controller)      (view)          (model)
                                            │
                                            ▼
                                   ┌─────────────────┐
                                   │  Database       │
                                   │  SQLite (dev)   │
                                   │  PostgreSQL(prod)│
                                   └─────────────────┘
```

---

## 3. Progettazione del database

Il database è composto da cinque tabelle collegate tra loro da relazioni uno-a-molti.

### Entità e attributi

**User** (utente)
- `id`, `username`, `email`, `password_hash`, `created_at`

**Workout** (allenamento)
- `id`, `name`, `workout_date`, `notes`, `created_at`, `user_id` (FK)

**Exercise** (esercizio)
- `id`, `name`, `sets`, `reps`, `weight`, `workout_id` (FK)

**Meal** (pasto)
- `id`, `name`, `meal_type`, `meal_date`, `calories`, `protein`, `carbs`, `fat`, `user_id` (FK)

**Measurement** (misurazione del peso)
- `id`, `measure_date`, `weight_kg`, `notes`, `user_id` (FK)

### Relazioni

- Un **User** ha molti **Workout**, molti **Meal** e molte **Measurement** (1:N).
- Un **Workout** ha molti **Exercise** (1:N).
- L'eliminazione di un utente o di un allenamento elimina automaticamente i dati collegati (`cascade='all, delete-orphan'`).

### Diagramma E-R (semplificato)

```
User (1) ──< (N) Workout (1) ──< (N) Exercise
  │
  ├──< (N) Meal
  │
  └──< (N) Measurement
```

---

## 4. Funzionalità implementate

### 4.1 Autenticazione e sicurezza
La gestione degli utenti usa la libreria **Flask-Login**. Le password non vengono mai salvate in chiaro: viene memorizzato solo l'**hash** generato con `generate_password_hash()` di Werkzeug. A ogni accesso, la password inserita viene confrontata con l'hash tramite `check_password_hash()`.

Le pagine riservate sono protette dal decoratore `@login_required`: un utente non autenticato che prova ad accedervi viene reindirizzato alla pagina di login. Inoltre, ogni operazione controlla che la risorsa appartenga effettivamente all'utente loggato (`if risorsa.user_id != current_user.id`), impedendo a un utente di vedere o modificare i dati di un altro.

### 4.2 Gestione allenamenti
L'utente può creare allenamenti e aggiungervi esercizi specificando serie, ripetizioni e peso. L'applicazione calcola automaticamente il **volume di lavoro** (serie × ripetizioni × peso), un indicatore usato in palestra per quantificare il carico totale di una sessione. Il calcolo è implementato come `@property` nei modelli, quindi è sempre coerente e aggiornato.

### 4.3 Diario alimentare
I pasti vengono registrati con calorie e macronutrienti e raggruppati per giorno. Per ogni giornata l'app calcola i totali di calorie, proteine, carboidrati e grassi. Il raggruppamento è realizzato lato server con un `defaultdict`.

### 4.4 Monitoraggio del peso e dashboard
Il peso corporeo viene registrato con la relativa data. Nella dashboard e nella pagina dedicata, i dati vengono passati ai grafici di **Chart.js** tramite il filtro Jinja2 `| tojson`, che converte le liste Python in array JavaScript. I grafici realizzati sono: linea (peso), barre (allenamenti e calorie settimanali) e ciambella (macronutrienti).

### 4.5 Esportazione dati
Gli allenamenti possono essere esportati in formato **CSV** tramite la libreria standard `csv` di Python, generando il file in memoria con `io.StringIO` e restituendolo come download.

---

## 5. Dallo sviluppo alla produzione

### 5.1 Server WSGI
In sviluppo l'app gira con il server integrato di Flask (`python run.py`). In produzione questo server non è adatto (è single-thread e non sicuro), perciò si usa **Gunicorn**, un server WSGI professionale, avviato con `gunicorn run:app`.

### 5.2 Variabili d'ambiente
I dati sensibili (in particolare la `SECRET_KEY`) non sono scritti nel codice ma letti dalle **variabili d'ambiente** con `os.environ.get()`. In locale sono salvate nel file `.env` (letto dalla libreria `python-dotenv`), che è escluso da Git tramite `.gitignore`. In produzione vengono impostate nel pannello di Render.

### 5.3 Deploy su Render
Il deploy avviene su **Render.com** (piattaforma PaaS). Il file `render.yaml` descrive la configurazione del servizio: comando di build (`pip install -r requirements.txt && python setup_db.py`) e comando di avvio (`gunicorn run:app`). Ogni `git push` su GitHub attiva un nuovo deploy automatico (Continuous Deployment).

### 5.4 Problema dei dati effimeri
Il piano gratuito di Render usa un disco effimero: a ogni riavvio il file SQLite viene azzerato. La soluzione professionale è collegare un database **PostgreSQL** esterno, che persiste indipendentemente dai riavvii. Il codice è già predisposto: legge `DATABASE_URL` dall'ambiente e, se presente, usa PostgreSQL al posto di SQLite.

---

## 6. Tecnologie utilizzate

| Ambito | Strumento | Motivazione |
|--------|-----------|-------------|
| Linguaggio | Python 3 | Linguaggio del corso, ampio ecosistema |
| Framework web | Flask | Leggero e adatto alla didattica |
| ORM / Database | SQLAlchemy + SQLite/PostgreSQL | Permette di usare classi invece di SQL grezzo |
| Autenticazione | Flask-Login | Gestione standard di sessioni e login |
| Sicurezza password | Werkzeug | Hashing sicuro delle password |
| Server produzione | Gunicorn | Server WSGI stabile e performante |
| Frontend | Bootstrap 5 + Jinja2 | Interfaccia responsive con poco codice |
| Grafici | Chart.js | Grafici interattivi lato client |
| Hosting | Render.com | PaaS con piano gratuito e deploy automatico |

---

## 7. Possibili sviluppi futuri

- Recupero password via email.
- Obiettivi giornalieri di calorie e macronutrienti con barre di avanzamento.
- Database di alimenti precompilati per velocizzare l'inserimento dei pasti.
- Statistiche avanzate (es. record personali per esercizio).
- Supporto multilingua.

---

## 8. Conclusioni

Il progetto FitLog ha permesso di affrontare in modo completo lo sviluppo di un'applicazione web moderna: dalla progettazione del database relazionale, alla realizzazione del back-end con Flask, alla gestione sicura dell'autenticazione, fino al deployment in produzione su una piattaforma cloud. Particolare attenzione è stata posta alla separazione tra ambiente di sviluppo e produzione e alla protezione dei dati sensibili tramite variabili d'ambiente.