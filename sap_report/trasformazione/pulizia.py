"""Pulizia degli ordini: tipi, valori non validi e duplicati.

La deduplica avviene sul numero ordine (VBELN), non sui valori:
due ordini diversi con cliente, importo e data uguali restano entrambi.
"""

import logging

import pandas as pd

log = logging.getLogger(__name__)


def pulisci_ordini(df: pd.DataFrame) -> pd.DataFrame:
    iniziali = len(df)
    df = df.copy()

    df["VBELN"] = df["VBELN"].astype("string").str.strip().str.zfill(10)
    df["KUNNR"] = df["KUNNR"].astype("string").str.strip()
    df["GBSTK"] = df["GBSTK"].astype("string").str.strip().str.upper()
    df["AUDAT"] = pd.to_datetime(df["AUDAT"], errors="coerce")
    df["VDATU"] = pd.to_datetime(df["VDATU"], errors="coerce")
    df["NETWR"] = pd.to_numeric(df["NETWR"], errors="coerce")

    df = df.dropna(subset=["VBELN", "AUDAT", "NETWR"])
    df = df[df["NETWR"] > 0]
    df = df.drop_duplicates(subset=["VBELN"], keep="first")
    df = df.sort_values(["AUDAT", "VBELN"]).reset_index(drop=True)

    log.info("Pulizia: %d ordini in ingresso, %d validi", iniziali, len(df))
    return df
