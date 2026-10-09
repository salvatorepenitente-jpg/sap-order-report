from datetime import date

import pandas as pd
import pytest

from sap_report.sorgenti.base import COLONNE_ORDINI
from sap_report.sorgenti.csv_export import SorgenteCsv
from sap_report.sorgenti.mock import SorgenteMock
from sap_report.sorgenti.odata import SorgenteODataSAP
from sap_report.trasformazione.pulizia import pulisci_ordini

GIORNO = date(2026, 10, 8)


def test_mock_e_deterministico():
    a = SorgenteMock().leggi_ordini(GIORNO)
    b = SorgenteMock().leggi_ordini(GIORNO)
    pd.testing.assert_frame_equal(a, b)


def test_mock_usa_i_nomi_di_campo_sap():
    df = SorgenteMock().leggi_ordini(GIORNO)
    assert list(df.columns) == COLONNE_ORDINI


def test_mock_contiene_errori_da_pulire():
    grezzi = SorgenteMock().leggi_ordini(GIORNO)
    assert len(pulisci_ordini(grezzi)) < len(grezzi)


def test_csv_legge_le_colonne_sap(tmp_path):
    f = tmp_path / "export.csv"
    f.write_text(
        "VBELN,KUNNR,AUDAT,VDATU,NETWR,WAERK,GBSTK\n"
        "0000000001,100245,2026-10-08,2026-10-15,100.00,EUR,A\n",
        encoding="utf-8",
    )
    df = SorgenteCsv(f).leggi_ordini(GIORNO)
    assert len(df) == 1
    assert list(df.columns) == COLONNE_ORDINI


def test_csv_senza_colonne_richieste_da_errore(tmp_path):
    f = tmp_path / "errato.csv"
    f.write_text("a,b\n1,2\n", encoding="utf-8")
    with pytest.raises(ValueError):
        SorgenteCsv(f).leggi_ordini(GIORNO)


def test_odata_non_ancora_implementato():
    with pytest.raises(NotImplementedError):
        SorgenteODataSAP().leggi_ordini(GIORNO)
