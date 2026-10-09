"""Sorgente di dati fittizi: genera ordini con i nomi di campo SAP.

I dati sono deterministici (stesso seme = stessi ordini) e includono
qualche errore voluto (duplicato, valore mancante) per testare la pulizia.
"""

import random
from datetime import date, timedelta

import pandas as pd

from .base import COLONNE_ORDINI, SorgenteOrdini

CLIENTI = [100245, 100311, 100402, 100587, 100640, 100712]
STATI = ["A", "B", "C"]  # A = aperto, B = parziale, C = completato
PESI_STATI = [0.5, 0.2, 0.3]


class SorgenteMock(SorgenteOrdini):
    def __init__(self, seme: int = 42, ordini_al_giorno: int = 25):
        self.seme = seme
        self.ordini_al_giorno = ordini_al_giorno

    def leggi_ordini(self, data: date) -> pd.DataFrame:
        rng = random.Random(f"{self.seme}-{data.isoformat()}")
        base = int(data.strftime("%Y%m%d")) * 100  # numeri ordine unici per giorno

        righe = []
        for i in range(self.ordini_al_giorno):
            righe.append(
                {
                    "VBELN": f"{base + i:010d}",
                    "KUNNR": str(rng.choice(CLIENTI)),
                    "AUDAT": data,
                    "VDATU": data + timedelta(days=rng.randint(-3, 14)),
                    "NETWR": round(rng.uniform(50, 5000), 2),
                    "WAERK": "EUR",
                    "GBSTK": rng.choices(STATI, weights=PESI_STATI)[0],
                }
            )
        df = pd.DataFrame(righe, columns=COLONNE_ORDINI)

        # Errori voluti: un duplicato esatto e un valore mancante
        df = pd.concat([df, df.iloc[[0]]], ignore_index=True)
        df.loc[3, "NETWR"] = None
        return df
