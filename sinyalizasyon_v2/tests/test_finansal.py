# -*- coding: utf-8 -*-
"""finansal.py testleri — Katman B modelleri (formüller ajanla doğrulandı).

Sayısal altın değerler bağımsız araştırma ajanı tarafından elle hesaplanıp
teyit edildi (Altman Z''=3.144 güvenli, EMS=6.394; Z'=1.779 gri).
"""
import dataclasses

import pytest

from sinyal_v2.finansal import (BeneishGirdi, FinansalVeri, altman_z2,
                                altman_z_ozel, beneish_m, merton_dd, ohlson_o,
                                piotroski_f)

# Ajan tarafından doğrulanan çalışılmış örnek girdileri
ORNEK = FinansalVeri(
    toplam_aktif=1000, donen_varlik=500, kisa_vadeli_borc=300, toplam_borc=600,
    gecmis_yil_karlari=100, faiz_vergi_oncesi_kar=120, satislar=900, net_kar=80)


def test_altman_z2_altin_deger():
    r = altman_z2(ORNEK)
    assert r is not None
    assert r.skor == 3.144                     # ajan doğrulaması
    assert r.bolge == "güvenli"                # >2.6
    assert r.ayrinti["ems_rating_esdegeri"] == 6.394   # 3.144 + 3.25


def test_altman_z_ozel_altin_deger():
    r = altman_z_ozel(ORNEK)
    assert r is not None
    assert r.skor == 1.779
    assert r.bolge == "gri"                     # 1.23–2.9


def test_altman_gecersiz_girdi_none():
    kotu = FinansalVeri(toplam_aktif=0, donen_varlik=0, kisa_vadeli_borc=0,
                        toplam_borc=0, gecmis_yil_karlari=0,
                        faiz_vergi_oncesi_kar=0, satislar=0, net_kar=0)
    assert altman_z2(kotu) is None
    assert altman_z_ozel(kotu) is None


def _fv(ta, dv, kvb, uvb, bk, sat, nk, cfo, hisse):
    return FinansalVeri(
        toplam_aktif=ta, donen_varlik=dv, kisa_vadeli_borc=kvb, toplam_borc=uvb + kvb,
        gecmis_yil_karlari=0, faiz_vergi_oncesi_kar=nk, satislar=sat, net_kar=nk,
        faaliyet_nakit_akisi=cfo, brut_kar=bk, uzun_vadeli_borc=uvb, hisse_adedi=hisse)


def test_piotroski_tam_puan():
    onceki = _fv(1000, 400, 300, 200, 200, 800, 50, 40, 100)
    cari = _fv(1100, 600, 300, 150, 350, 1000, 110, 150, 100)
    r = piotroski_f(cari, onceki)
    assert r is not None
    assert r.skor == 9.0 and r.bolge == "güvenli"
    assert all(r.ayrinti.values())             # 9 kriterin hepsi sağlandı


def test_ohlson_altin_deger():
    # Ajan-doğrulanmış çalışılmış örnek: O=0.669, P=0.6614 (Model 1)
    cari = FinansalVeri(
        toplam_aktif=1000, donen_varlik=500, kisa_vadeli_borc=300,
        toplam_borc=600, gecmis_yil_karlari=100, faiz_vergi_oncesi_kar=80,
        satislar=900, net_kar=50, ffo=90)
    onceki = FinansalVeri(
        toplam_aktif=950, donen_varlik=480, kisa_vadeli_borc=290,
        toplam_borc=560, gecmis_yil_karlari=90, faiz_vergi_oncesi_kar=70,
        satislar=850, net_kar=40, ffo=80)
    r = ohlson_o(cari, onceki, gsyh_deflator=100)
    assert r is not None
    assert r.skor == 0.669
    assert r.ayrinti["olasilik"] == 0.6614
    assert r.bolge == "sıkıntı"                 # P > 0.5


def test_ohlson_saglam_firma_guvenli():
    saglam = FinansalVeri(
        toplam_aktif=1000, donen_varlik=800, kisa_vadeli_borc=100,
        toplam_borc=100, gecmis_yil_karlari=400, faiz_vergi_oncesi_kar=250,
        satislar=1200, net_kar=200, ffo=250)
    onceki = FinansalVeri(
        toplam_aktif=950, donen_varlik=750, kisa_vadeli_borc=100,
        toplam_borc=100, gecmis_yil_karlari=350, faiz_vergi_oncesi_kar=220,
        satislar=1100, net_kar=180, ffo=220)
    r = ohlson_o(saglam, onceki, gsyh_deflator=100)
    assert r is not None and r.bolge == "güvenli"
    assert r.ayrinti["olasilik"] < 0.038


def test_ohlson_eksik_ffo_none():
    fv = FinansalVeri(
        toplam_aktif=1000, donen_varlik=500, kisa_vadeli_borc=300,
        toplam_borc=600, gecmis_yil_karlari=100, faiz_vergi_oncesi_kar=80,
        satislar=900, net_kar=50)                # ffo/cfo yok
    assert ohlson_o(fv, fv, gsyh_deflator=100) is None


# Nötr Beneish girdisi (iki yıl aynı, NI=CFO): tüm endeksler 1, TATA=0
_BENEISH_NOTR = BeneishGirdi(
    satislar=1000, satis_maliyeti=600, ticari_alacaklar=200, donen_varlik=500,
    maddi_duran_varlik=300, toplam_aktif=1000, amortisman=50,
    faaliyet_giderleri=100, toplam_borc=400, net_kar=100,
    faaliyet_nakit_akisi=100)


def test_beneish_notr_temiz():
    # tüm endeksler 1, TATA=0 → M = -4.84 + (katsayı toplamı) = -2.48
    r = beneish_m(_BENEISH_NOTR, _BENEISH_NOTR)
    assert r is not None
    assert r.skor == pytest.approx(-2.48, abs=0.01)
    assert r.bolge == "temiz"                  # M < -1.78


def test_beneish_yuksek_tahakkuk_supheli():
    # net kâr nakit akışını çok aşarsa (TATA=0.2) → M > -1.78
    cari = dataclasses.replace(_BENEISH_NOTR, net_kar=300)  # NI-CFO=200
    r = beneish_m(cari, _BENEISH_NOTR)
    assert r is not None
    assert r.ayrinti["TATA"] == pytest.approx(0.2, abs=0.001)
    assert r.skor == pytest.approx(-1.544, abs=0.01)
    assert r.bolge == "şüpheli"                # M > -1.78


def test_beneish_gecersiz_girdi_none():
    kotu = dataclasses.replace(_BENEISH_NOTR, satislar=0)
    assert beneish_m(kotu, _BENEISH_NOTR) is None


def test_merton_saglam_firma_guvenli():
    # E=1000, σE=0.4, D=500, r=0.10, T=1 → DD≈3.627, PD çok küçük
    r = merton_dd(1000, 0.4, 500, 0.10, 1.0)
    assert r is not None
    assert r.skor == pytest.approx(3.627, abs=0.01)
    assert r.bolge == "güvenli"
    assert r.ayrinti["temerrut_olasiligi"] < 0.01


def test_merton_riskli_firma_sikinti():
    # düşük özkaynak + yüksek volatilite + yüksek borç → düşük DD, yüksek PD
    r = merton_dd(100, 0.8, 900, 0.10, 1.0)
    assert r is not None
    assert r.bolge == "sıkıntı"
    assert r.ayrinti["temerrut_olasiligi"] > 0.10


def test_merton_gecersiz_girdi_none():
    assert merton_dd(0, 0.4, 500) is None       # piyasa özkaynağı yok
    assert merton_dd(1000, 0, 500) is None       # volatilite yok


def test_piotroski_eksik_veri_none():
    tam = _fv(1000, 400, 300, 200, 200, 800, 50, 40, 100)
    eksik = FinansalVeri(
        toplam_aktif=1000, donen_varlik=400, kisa_vadeli_borc=300,
        toplam_borc=500, gecmis_yil_karlari=0, faiz_vergi_oncesi_kar=50,
        satislar=800, net_kar=50)             # CFO/brüt/UVB/hisse yok
    assert piotroski_f(eksik, tam) is None
