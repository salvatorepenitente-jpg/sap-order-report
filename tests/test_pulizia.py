import pandas as pd

from sap_report.trasformazione.pulizia import pulisci_ordini


def _ordine(**campi):
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


def test_deduplica_per_numero_ordine():
    df = pd.DataFrame([_ordine(), _ordine()])
    assert len(pulisci_ordini(df)) == 1


def test_ordini_diversi_con_stessi_valori_restano_entrambi():
    df = pd.DataFrame([_ordine(VBELN="0000000001"), _ordine(VBELN="0000000002")])
    assert len(pulisci_ordini(df)) == 2


def test_valori_non_validi_vengono_scartati():
    df = pd.DataFrame(
        [
            _ordine(NETWR="abc"),
            _ordine(VBELN="0000000002", NETWR=None),
            _ordine(VBELN="0000000003", NETWR="-5"),
            _ordine(VBELN="0000000004"),
        ]
    )
    assert list(pulisci_ordini(df)["VBELN"]) == ["0000000004"]


def test_numero_ordine_e_stato_normalizzati():
    df = pd.DataFrame([_ordine(VBELN="  1  ", GBSTK=" c ")])
    pulito = pulisci_ordini(df)
    assert pulito.loc[0, "VBELN"] == "0000000001"
    assert pulito.loc[0, "GBSTK"] == "C"
