# SAP Order Report

Progetto di **process automation** in Python che genera ogni giorno un report Excel degli ordini di vendita.

Il progetto funziona con **dati fittizi** e usa i nomi di campo standard di SAP (`VBELN`, `KUNNR`, `AUDAT`, `VDATU`, `NETWR`, `WAERK`, `GBSTK`). La sorgente dei dati è separata dal resto del codice, quindi si può collegare a SAP senza modificare il report.

## Cosa produce il report

Un file `output/report_ordini_AAAA-MM-GG.xlsx` con cinque fogli:

| Foglio | Contenuto |
|---|---|
| **Riepilogo** | ordini ricevuti, valore totale, confronto con il giorno precedente, ordini in ritardo |
| **Per cliente** | ordini e valore per cliente |
| **Per stato** | ordini e valore per stato (aperto, parziale, completato) |
| **Ordini in ritardo** | ordini non completati con data di consegna già superata |
| **Dettaglio ordini** | tutti gli ordini del giorno, dopo la pulizia |

## Come iniziare

Servono Python 3.10 o superiore.

```bash
git clone https://github.com/TUO-USERNAME/sap-order-report.git
cd sap-order-report

python -m venv .venv
source .venv/bin/activate        # su Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env             # su Windows: copy .env.example .env
python -m sap_report --sorgente mock --data 2026-10-08
```

Il report compare in `output/`.

## Sorgenti dei dati

| Sorgente | Stato | Come si usa |
|---|---|---|
| `mock` | pronta | dati fittizi generati dal codice, per sviluppo e test |
| `csv` | pronta | export manuale da SAP (es. transazione VA05) salvato in CSV |
| `odata` | da fare (fase 2) | connessione all'API S/4HANA `API_SALES_ORDER_SRV` |

Per usare un export CSV:

```bash
python -m sap_report --sorgente csv --file dati_input/export.csv --data 2026-10-08
```

Il CSV deve avere le colonne `VBELN, KUNNR, AUDAT, VDATU, NETWR, WAERK, GBSTK`, con le date in formato `AAAA-MM-GG` e i decimali con il punto.

## Test

```bash
pytest
```

I test girano anche su GitHub a ogni push, tramite GitHub Actions.

## Struttura

```
sap-order-report/
├── sap_report/
│   ├── main.py              # punto d'ingresso
│   ├── config.py            # configurazione da variabili d'ambiente
│   ├── sorgenti/            # da dove arrivano gli ordini
│   ├── trasformazione/      # pulizia dei dati e calcolo dei KPI
│   └── report/              # scrittura del file Excel
├── tests/
├── .env.example
└── requirements.txt
```

Per aggiungere una nuova sorgente basta creare una classe in `sap_report/sorgenti/` che estende `SorgenteOrdini` e restituisce un DataFrame con le colonne sopra.

## Roadmap

- [x] Struttura modulare con sorgenti intercambiabili
- [x] Dati fittizi e test automatici
- [ ] Connessione OData a SAP S/4HANA (fase 2)
- [ ] Esecuzione giornaliera pianificata (Utilità di pianificazione di Windows o cron)
- [ ] Invio del report via email
