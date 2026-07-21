# -*- coding: utf-8 -*-
"""Katman A+B fusion testleri (skor.firma_skoru_hibrit)."""
from datetime import datetime, timedelta

from sinyal_v2.finansal import FinansalVeri
from sinyal_v2.model import KaynakTipi, Siddet, Sinyal
from sinyal_v2.skor import finansal_risk, firma_skoru, firma_skoru_hibrit

SIMDI = datetime(2026, 6, 1)


def _sinyal(agirlik, kategori_id="iflas"):
    return Sinyal(
        firma_id="c1", kategori_id=kategori_id, kategori=kategori_id.upper(),
        siddet=Siddet.agirliktan(agirlik), agirlik=agirlik,
        tarih=SIMDI - timedelta(days=30), kaynak_kaydi_id="k",
        kaynak_tipi=KaynakTipi.KAP, gerekce="", iyilesme=False)


# Altman Z'' sıkıntı bölgesine düşen firma (negatif işletme sermayesi + zarar)
_SIKINTI = FinansalVeri(
    toplam_aktif=1000, donen_varlik=100, kisa_vadeli_borc=400, toplam_borc=900,
    gecmis_yil_karlari=-200, faiz_vergi_oncesi_kar=-50, satislar=300, net_kar=-80)


def test_finansal_risk_sikinti():
    r = finansal_risk(_SIKINTI)
    assert r is not None
    risk, aciklama = r
    assert risk == 80.0                        # sıkıntı bölgesi tabanı
    assert any("Altman" in a for a in aciklama)


def test_hibrit_finansal_veri_yoksa_katman_a():
    a = firma_skoru([_sinyal(10)], SIMDI)
    h = firma_skoru_hibrit([_sinyal(10)], finansal_veri=None, simdi=SIMDI)
    assert h.skor == a.skor and h.katman_b is None


def test_hibrit_finansal_riski_ekler():
    # Katman A = 24.0 (tek iflas), Katman B = 80 → 0.55*24 + 0.45*80 = 49.2
    h = firma_skoru_hibrit([_sinyal(10)], finansal_veri=_SIKINTI, simdi=SIMDI)
    assert h.katman_a == 24.0
    assert h.katman_b == 80.0
    assert h.skor == 49.2 and h.notu == "D"    # olay-tek D'den (24=C) yükseldi
    assert h.guven == 0.85
    assert any("fusion" in a for a in h.aciklama)


def test_hibrit_olaysiz_ama_finansal_sikinti():
    # hiç olay yok ama finansal sıkıntı → skor yalnız Katman B'den gelir
    h = firma_skoru_hibrit([], finansal_veri=_SIKINTI, simdi=SIMDI)
    assert h.katman_a == 0.0 and h.katman_b == 80.0
    assert h.skor == 36.0 and h.notu == "C"    # 0.45*80
