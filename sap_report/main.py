"""Punto d'ingresso: estrae, pulisce, calcola i KPI e scrive il report.

Esempi:
    python -m sap_report --sorgente mock --data 2026-10-08
    python -m sap_report --sorgente csv --file export.csv --data 2026-10-08
"""

import argparse
import logging
from datetime import date, timedelta
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv

from sap_report.config import carica_config
from sap_report.report.excel import scrivi_report
from sap_report.sorgenti.base import SorgenteOrdini
from sap_report.sorgenti.csv_export import SorgenteCsv
from sap_report.sorgenti.mock import SorgenteMock
from sap_report.sorgenti.odata import SorgenteODataSAP
from sap_report.trasformazione.metriche import calcola_kpi
from sap_report.trasformazione.pulizia import pulisci_ordini

log = logging.getLogger(__name__)

SORGENTI = ["mock", "csv", "odata"]


def crea_sorgente(nome: str, file: Path | None) -> SorgenteOrdini:
    if nome == "mock":
        return SorgenteMock()
    if nome == "csv":
        if file is None:
            raise ValueError("Con --sorgente csv serve anche --file")
        return SorgenteCsv(file)
    if nome == "odata":
        return SorgenteODataSAP()
    raise ValueError(f"Sorgente sconosciuta: {nome}")


def genera_report(sorgente: SorgenteOrdini, data: date, cartella_output: Path) -> Path:
    # Carico anche il giorno precedente per il confronto
    grezzi = pd.concat(
        [sorgente.leggi_ordini(data - timedelta(days=1)), sorgente.leggi_ordini(data)],
        ignore_index=True,
    )
    ordini = pulisci_ordini(grezzi)
    kpi = calcola_kpi(ordini, data)
    dettaglio = ordini[ordini["AUDAT"].dt.normalize() == pd.Timestamp(data)]

    destinazione = cartella_output / f"report_ordini_{data.isoformat()}.xlsx"
    return scrivi_report(data, kpi, dettaglio, destinazione)


def main(argv: list[str] | None = None) -> None:
    load_dotenv()
    config = carica_config()

    parser = argparse.ArgumentParser(description="Report giornaliero degli ordini SAP")
    parser.add_argument("--sorgente", choices=SORGENTI, default=config.sorgente)
    parser.add_argument("--file", type=Path, help="export CSV (solo con --sorgente csv)")
    parser.add_argument("--data", type=date.fromisoformat, default=date.today(), help="AAAA-MM-GG")
    parser.add_argument("--output", type=Path, default=config.output_dir)
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    sorgente = crea_sorgente(args.sorgente, args.file)
    destinazione = genera_report(sorgente, args.data, args.output)
    log.info("Report salvato in %s", destinazione)


if __name__ == "__main__":
    main()
