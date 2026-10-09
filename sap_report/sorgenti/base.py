"""Interfaccia comune per tutte le sorgenti di ordini.

Il resto del progetto non sa da dove arrivano i dati: riceve sempre
un DataFrame con le colonne di COLONNE_ORDINI, che usano i nomi dei
campi standard SAP (VBAK/VBAP).
"""

from abc import ABC, abstractmethod
from datetime import date

import pandas as pd

COLONNE_ORDINI = ["VBELN", "KUNNR", "AUDAT", "VDATU", "NETWR", "WAERK", "GBSTK"]


class SorgenteOrdini(ABC):
    @abstractmethod
    def leggi_ordini(self, data: date) -> pd.DataFrame:
        """Restituisce gli ordini della data indicata.

        Può restituire anche righe di altre date: il filtro per giorno
        viene fatto dalla trasformazione.
        """
