"""Placeholder per la fase 2: connessione all'API OData di SAP S/4HANA.

Quando sarà pronta, questa classe chiamerà il servizio standard degli
ordini di vendita (API_SALES_ORDER_SRV) e restituirà lo stesso DataFrame
delle altre sorgenti. Il resto del progetto non va modificato.
"""

from datetime import date

import pandas as pd

from .base import SorgenteOrdini


class SorgenteODataSAP(SorgenteOrdini):
    def leggi_ordini(self, data: date) -> pd.DataFrame:
        raise NotImplementedError(
            "Connessione OData non ancora implementata (fase 2, vedi README)."
        )
