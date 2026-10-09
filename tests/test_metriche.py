from datetime import date, timedelta

import pandas as pd
import pytest

from sap_report.sorgenti.mock import SorgenteMock
from sap_report.trasformazione.metriche import calcola_kpi
from sap_report.trasformazione.pulizia import pulisci_ordini

GIORNO = date(2026, 10, 8)


def _riga(**campi):
    riga = {
        "VBELN": "0000000001",
        "KUNNR": "100245",
        "AUDAT": "2026-10-08",
        "VDATU": "2026-10-15",
        "NETWR": "100.00",
        "WAERK": "EUR",
        "GBSTK": "A",
    }
    riga.update(campi)
    return riga


def test_totali_coerenti_con_il_dettaglio():
    m = SorgenteMock()
    grezzi = pd.concat(
        [m.leggi_ordini(GIORNO - timedelta(days=1)), m.leggi_ordini(GIORNO)],
        ignore_index=True,
    )
    ordini = pulisci_ordini(grezzi)
    kpi = calcola_kpi(ordini, GIORNO)

    dettaglio = ordini[ordini["AUDAT"].dt.normalize() == pd.Timestamp(GIORNO)]
    assert kpi["ordini_giorno"] > 0
    assert kpi["ordini_giorno"] == len(dettaglio)
    assert kpi["valore_giorno"] == pytest.approx(dettaglio["NETWR"].sum())
    assert kpi["per_cliente"]["Ordini"].sum() == kpi["ordini_giorno"]
    assert kpi["per_stato"]["Ordini"].sum() == kpi["ordini_giorno"]


def test_variazione_è_none_senza_giorno_precedente():
    ordini = pulisci_ordini(pd.DataFrame([_riga()]))
    kpi = calcola_kpi(ordini, GIORNO)
    assert kpi["ordini_giorno_prima"] == 0
    assert kpi["variazione_ordini_pct"] is None


def test_variazione_percentuale_tra_due_giorni():
    ieri = _riga(VBELN="0000000001", AUDAT="2026-10-07")
    oggi_1 = _riga(VBELN="0000000002")
    oggi_2 = _riga(VBELN="0000000003")
    ordini = pulisci_ordini(pd.DataFrame([ieri, oggi_1, oggi_2]))
    kpi = calcola_kpi(ordini, GIORNO)
    assert kpi["variazione_ordini_pct"] == 100.0


def test_ordini_in_ritardo_esclude_i_completati():
    in_ritardo = _riga(VBELN="0000000001", VDATU="2026-10-01", GBSTK="A")
    completato = _riga(VBELN="0000000002", VDATU="2026-10-01", GBSTK="C")
    ordini = pulisci_ordini(pd.DataFrame([in_ritardo, completato]))
    kpi = calcola_kpi(ordini, GIORNO)
    assert kpi["ordini_in_ritardo"] == 1
    assert list(kpi["in_ritardo"]["Ordine"]) == ["0000000001"]
