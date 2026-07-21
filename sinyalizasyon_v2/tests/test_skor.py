# -*- coding: utf-8 -*-
"""skor.py birim testleri — Katman A skorlama (V1 mantığı)."""
from datetime import datetime, timedelta

from sinyal_v2.model import KaynakTipi, Siddet, Sinyal
from sinyal_v2.skor import (SCORE_GAIN, firma_skoru, guncellik_faktoru,
                            not_ver)

SIMDI = datetime(2026, 6, 1)


def _sinyal(agirlik, gun_once, kategori_id="iflas", iyilesme=False):
    return Sinyal(
        firma_id="c1", kategori_id=kategori_id, kategori=kategori_id.upper(),
        siddet=Siddet.agirliktan(agirlik), agirlik=agirlik,
        tarih=SIMDI - timedelta(days=gun_once), kaynak_kaydi_id="k",
        kaynak_tipi=KaynakTipi.KAP, gerekce="", iyilesme=iyilesme)


def test_guncellik_kademeleri():
    assert guncellik_faktoru(SIMDI - timedelta(days=30), SIMDI) == 1.0
    assert guncellik_faktoru(SIMDI - timedelta(days=200), SIMDI) == 0.75
    assert guncellik_faktoru(SIMDI - timedelta(days=600), SIMDI) == 0.5
    assert guncellik_faktoru(SIMDI - timedelta(days=1000), SIMDI) == 0.3
    assert guncellik_faktoru(datetime.min, SIMDI) == 0.3


def test_not_esikleri():
    assert not_ver(70)[0] == "E"
    assert not_ver(45)[0] == "D"
    assert not_ver(20)[0] == "C"
    assert not_ver(1)[0] == "B"
    assert not_ver(0)[0] == "A"


def test_tek_sinyal_skor():
    r = firma_skoru([_sinyal(10, 30)], SIMDI)
    assert r.skor == round(10 * 1.0 * SCORE_GAIN, 1)   # 24.0
    assert r.notu == "C"
    assert r.katman_b is None and r.guven == 0.6
    assert any("olay verisine" in a for a in r.aciklama)


def test_kategori_ici_sonumleme():
    # aynı kategoride 2 bulgu: 24.0 + 8.4 = 32.4
    r = firma_skoru([_sinyal(10, 30), _sinyal(10, 30)], SIMDI)
    assert r.skor == 32.4
    assert r.notu == "C"


def test_iki_kategori_toplanir():
    r = firma_skoru([_sinyal(10, 30, "iflas"),
                     _sinyal(10, 30, "temerrut")], SIMDI)
    assert r.skor == 48.0 and r.notu == "D"


def test_iyilesme_skora_girmez():
    r = firma_skoru([_sinyal(10, 30, iyilesme=True)], SIMDI)
    assert r.skor == 0.0 and r.notu == "A" and r.guven == 1.0


def test_bulgu_varsa_temiz_olamaz_b_ye_yukselir():
    # çok eski, düşük ağırlık → skor < 1 ama bulgu var → A yerine B
    r = firma_skoru([_sinyal(1, 1000)], SIMDI)   # 1*0.3*2.4 = 0.72
    assert r.skor < 1.0 and r.notu == "B"


def test_bulgu_yoksa_temiz():
    r = firma_skoru([], SIMDI)
    assert r.skor == 0.0 and r.notu == "A" and r.guven == 1.0
