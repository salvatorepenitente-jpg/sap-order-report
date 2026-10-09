"""Scrittura del report giornaliero in Excel."""

from datetime import date
from pathlib import Path

import pandas as pd


def _date_leggibili(tabella: pd.DataFrame) -> pd.DataFrame:
    """Converte le colonne datetime in sole date, più leggibili in Excel."""
    tabella = tabella.copy()
    for colonna in tabella.columns:
        if pd.api.types.is_datetime64_any_dtype(tabella[colonna]):
            tabella[colonna] = tabella[colonna].dt.date
    return tabella


def _adatta_colonne(ws) -> None:
    for colonna in ws.columns:
        lunghezza = max(len(str(cella.value)) if cella.value is not None else 0 for cella in colonna)
        ws.column_dimensions[colonna[0].column_letter].width = min(max(lunghezza + 2, 12), 45)


def scrivi_report(data: date, kpi: dict, dettaglio: pd.DataFrame, destinazione: str | Path) -> Path:
    destinazione = Path(destinazione)
    destinazione.parent.mkdir(parents=True, exist_ok=True)

    variazione = kpi["variazione_ordini_pct"]
    riepilogo = pd.DataFrame(
        [
            ("Data", data.isoformat()),
            ("Ordini ricevuti", kpi["ordini_giorno"]),
            ("Valore totale (EUR)", round(kpi["valore_giorno"], 2)),
            ("Ordini giorno precedente", kpi["ordini_giorno_prima"]),
            ("Valore giorno precedente (EUR)", round(kpi["valore_giorno_prima"], 2)),
            ("Variazione ordini (%)", variazione if variazione is not None else "n.d."),
            ("Ordini in ritardo", kpi["ordini_in_ritardo"]),
        ],
        columns=["Indicatore", "Valore"],
    )

    fogli = {
        "Per cliente": kpi["per_cliente"],
        "Per stato": kpi["per_stato"],
        "Ordini in ritardo": _date_leggibili(kpi["in_ritardo"]),
        "Dettaglio ordini": _date_leggibili(dettaglio),
    }

    with pd.ExcelWriter(destinazione, engine="openpyxl") as writer:
        riepilogo.to_excel(writer, sheet_name="Riepilogo", index=False)
        for nome, tabella in fogli.items():
            tabella.to_excel(writer, sheet_name=nome, index=False)
        for ws in writer.book.worksheets:
            _adatta_colonne(ws)

    return destinazione
