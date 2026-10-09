"""Sorgente che legge un export manuale degli ordini da SAP (file CSV).

Il file deve avere le colonne di COLONNE_ORDINI, con le date in formato
ISO (AAAA-MM-GG) e i decimali con il punto.
"""

from datetime import date
from pathlib import Path

import pandas as pd

from .base import COLONNE_ORDINI, SorgenteOrdini


class SorgenteCsv(SorgenteOrdini):
    def __init__(self, percorso: str | Path):
        self.percorso = Path(percorso)

    def leggi_ordini(self, data: date) -> pd.DataFrame:
        if not self.percorso.exists():
            raise FileNotFoundError(f"File non trovato: {self.percorso}")

        df = pd.read_csv(self.percorso, dtype=str)
        df.columns = [c.strip().upper() for c in df.columns]

        mancanti = set(COLONNE_ORDINI) - set(df.columns)
        if mancanti:
            raise ValueError(f"Colonne mancanti nell'export: {sorted(mancanti)}")

        return df[COLONNE_ORDINI]
