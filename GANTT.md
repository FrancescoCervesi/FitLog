# Diagramma di Gantt — FitLog

```mermaid
gantt
    title Piano di lavoro — 5 settimane
    dateFormat YYYY-MM-DD
    axisFormat %d/%m

    section Analisi
    Analisi dei requisiti              :done, 2026-04-27, 2d
    Progettazione schema ER            :done, 2026-04-28, 2d
    Diagramma UML delle classi         :done, 2026-04-30, 1d
    Diagramma dei casi d uso           :done, 2026-04-30, 1d
    Configurazione ambiente Flask      :done, 2026-05-01, 1d

    section Sviluppo
    Modelli SQLAlchemy e setup_db      :done, 2026-05-04, 2d
    Application factory e config       :done, 2026-05-05, 1d
    Autenticazione (register/login)    :done, 2026-05-06, 2d
    Template base.html e navbar        :done, 2026-05-08, 1d
    Foglio di stile style.css          :done, 2026-05-08, 1d
    Gestione allenamenti ed esercizi   :done, 2026-05-11, 3d
    Diario alimentare (pasti)          :done, 2026-05-14, 2d
    Monitoraggio del peso              :done, 2026-05-18, 2d
    Dashboard e grafici Chart.js       :done, 2026-05-20, 3d
    Esportazione CSV e dati demo       :done, 2026-05-25, 2d

    section Rifinitura
    Documento dei requisiti            :done, 2026-05-27, 2d
    README e relazione tecnica         :done, 2026-05-28, 1d
    Testing e correzione bug           :done, 2026-05-29, 2d
    Deploy su Render                   :done, 2026-06-01, 1d
    Preparazione esposizione orale     :active, 2026-06-02, 1d
    Consegna finale                    :milestone, 2026-06-02, 0d
```

## Riepilogo fasi

| Fase | Periodo | Durata |
|------|---------|--------|
| Analisi | 27/04 – 01/05/2026 | ~1 settimana |
| Sviluppo | 04/05 – 26/05/2026 | ~3 settimane |
| Rifinitura | 27/05 – 02/06/2026 | ~1 settimana |
