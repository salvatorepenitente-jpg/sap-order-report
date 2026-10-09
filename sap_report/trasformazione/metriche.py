"""KPI giornalieri calcolati sugli ordini puliti."""

from datetime import date, timedelta

import pandas as pd

STATI = {"A": "Aperto", "B": "Parziale", "C": "Completato"}


def _ordini_del_giorno(ordini: pd.DataFrame, giorno: date) -> pd.DataFrame:
    return ordini[ordini["AUDAT"].dt.normalize() == pd.Timestamp(giorno)]


def calcola_kpi(ordini: pd.DataFrame, data: date) -> dict:
    oggi = _ordini_del_giorno(ordini, data)
    ieri = _ordini_del_giorno(ordini, data - timedelta(days=1))

    n_oggi, n_ieri = len(oggi), len(ieri)
    variazione = round((n_oggi - n_ieri) / n_ieri * 100, 1) if n_ieri else None

    per_cliente = (
        oggi.groupby("KUNNR")
        .agg(Ordini=("VBELN", "count"), Valore=("NETWR", "sum"))
        .reset_index()
        .rename(columns={"KUNNR": "Cliente", "Valore": "Valore (EUR)"})
        .sort_values("Valore (EUR)", ascending=False)
    )

    per_stato = (
        oggi.assign(Stato=oggi["GBSTK"].map(STATI).fillna("Sconosciuto"))
        .groupby("Stato")
        .agg(Ordini=("VBELN", "count"), Valore=("NETWR", "sum"))
        .reset_index()
        .rename(columns={"Valore": "Valore (EUR)"})
    )

    # Ordini non completati con data di consegna già superata
    in_ritardo = ordini[
        (ordini["VDATU"] < pd.Timestamp(data)) & (ordini["GBSTK"] != "C")
    ][["VBELN", "KUNNR", "VDATU", "GBSTK", "NETWR"]]
    in_ritardo = in_ritardo.rename(
        columns={
            "VBELN": "Ordine",
            "KUNNR": "Cliente",
            "VDATU": "Consegna prevista",
            "GBSTK": "Stato",
            "NETWR": "Valore (EUR)",
        }
    ).sort_values("Consegna prevista")

    return {
        "ordini_giorno": n_oggi,
        "valore_giorno": float(oggi["NETWR"].sum()),
        "ordini_giorno_prima": n_ieri,
        "valore_giorno_prima": float(ieri["NETWR"].sum()),
        "variazione_ordini_pct": variazione,
        "ordini_in_ritardo": len(in_ritardo),
        "per_cliente": per_cliente,
        "per_stato": per_stato,
        "in_ritardo": in_ritardo,
    }
