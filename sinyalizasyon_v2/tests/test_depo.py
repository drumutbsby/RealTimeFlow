# -*- coding: utf-8 -*-
"""depo.py birim testleri — SQLite kalıcılık round-trip."""
from datetime import datetime

from sinyal_v2.depo import Depo
from sinyal_v2.model import (Firma, KaynakKaydi, KaynakTipi, Siddet, Sinyal)


def test_firma_round_trip():
    d = Depo()
    f = Firma(canonical_id="c1", unvan="Test A.Ş.", vkn="8760047464",
              halka_acik=True, unvan_varyantlari=["Test AS", "Test Anonim"])
    d.firma_ekle(f)
    g = d.firma_getir("c1")
    assert g is not None
    assert g.unvan == "Test A.Ş." and g.vkn == "8760047464"
    assert g.halka_acik is True
    assert g.unvan_varyantlari == ["Test AS", "Test Anonim"]
    assert d.firma_ara_vkn("8760047464").canonical_id == "c1"


def test_kaynak_kaydi_ham_veri_ve_enum():
    d = Depo()
    d.firma_ekle(Firma(canonical_id="c1", unvan="X"))
    kk = KaynakKaydi(id="kap:5", firma_id="c1", kaynak_tipi=KaynakTipi.KAP,
                     orijinal_kimlik="5", cekim_zamani=datetime(2026, 3, 1, 9, 0),
                     kaynak_url="http://x", ham_veri={"title": "İflas", "n": 3})
    d.kaynak_kaydi_ekle(kk)
    g = d.kaynak_kaydi_getir("kap:5")
    assert g.kaynak_tipi is KaynakTipi.KAP          # enum round-trip
    assert g.ham_veri == {"title": "İflas", "n": 3}  # JSON + TR karakter
    assert g.cekim_zamani == datetime(2026, 3, 1, 9, 0)


def test_sinyal_ekle_ve_getir():
    d = Depo()
    d.firma_ekle(Firma(canonical_id="c1", unvan="X"))
    s = Sinyal(firma_id="c1", kategori_id="iflas", kategori="İflas / Tasfiye",
               siddet=Siddet.KRITIK, agirlik=10, tarih=datetime(2026, 2, 1),
               kaynak_kaydi_id="kap:5", kaynak_tipi=KaynakTipi.KAP,
               gerekce="'iflas' ifadesi", iyilesme=False)
    sid = d.sinyal_ekle(s)
    assert sid == 1
    liste = d.firma_sinyalleri("c1")
    assert len(liste) == 1
    assert liste[0].siddet is Siddet.KRITIK       # enum round-trip
    assert liste[0].iyilesme is False
    assert liste[0].kategori == "İflas / Tasfiye"


def test_bos_firma_sinyalleri():
    d = Depo()
    d.firma_ekle(Firma(canonical_id="c1", unvan="X"))
    assert d.firma_sinyalleri("c1") == []
