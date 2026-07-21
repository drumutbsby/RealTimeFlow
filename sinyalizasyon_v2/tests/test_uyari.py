# -*- coding: utf-8 -*-
"""uyari.py + depo skor tarihçesi testleri."""
from datetime import datetime

from sinyal_v2.depo import Depo
from sinyal_v2.model import Firma, SkorAnlik
from sinyal_v2.uyari import uyari_metni, uyari_uret, uyarilari_uret


def _skor(firma_id, skor, notu):
    return SkorAnlik(firma_id=firma_id, tarih=datetime(2026, 6, 1), skor=skor,
                     notu=notu, model_surumu="test")


def test_not_kotulesme_uyarisi():
    u = uyari_uret(_skor("c1", 20, "C"), _skor("c1", 50, "D"))
    assert u is not None
    assert any("kötüleşti" in s for s in u["sebepler"])
    assert any("arttı" in s for s in u["sebepler"])       # +30 ≥ eşik


def test_kucuk_degisim_uyari_yok():
    assert uyari_uret(_skor("c1", 20, "C"), _skor("c1", 25, "C")) is None


def test_yeni_firma_yuksek_risk():
    assert uyari_uret(None, _skor("c1", 60, "D")) is not None
    assert uyari_uret(None, _skor("c1", 5, "B")) is None   # yeni ama düşük risk


def test_iyilesme_uyari_uretmez():
    # not iyileşti (D→B), skor düştü → uyarı yok
    assert uyari_uret(_skor("c1", 55, "D"), _skor("c1", 10, "B")) is None


def test_uyarilari_uret_siralar_ve_metin():
    onceki = {"a": _skor("a", 10, "B")}
    yeni = {"a": _skor("a", 40, "C"), "b": _skor("b", 70, "E")}
    uyarilar = uyarilari_uret(onceki, yeni)
    assert [u["firma_id"] for u in uyarilar] == ["b", "a"]  # skora göre sıralı
    metin = uyari_metni(uyarilar)
    assert "2 UYARI" in metin and uyari_metni([]) == "Yeni uyarı yok."


def test_depo_skor_tarihcesi():
    d = Depo()
    d.firma_ekle(Firma(canonical_id="c1", unvan="X"))
    assert d.son_skor("c1") is None
    d.skor_kaydet(_skor("c1", 20, "C"))
    d.skor_kaydet(_skor("c1", 45, "D"))
    son = d.son_skor("c1")
    assert son.skor == 45 and son.notu == "D"              # en son kayıt
