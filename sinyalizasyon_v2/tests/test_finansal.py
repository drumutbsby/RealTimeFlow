# -*- coding: utf-8 -*-
"""finansal.py testleri — Katman B modelleri (formüller ajanla doğrulandı).

Sayısal altın değerler bağımsız araştırma ajanı tarafından elle hesaplanıp
teyit edildi (Altman Z''=3.144 güvenli, EMS=6.394; Z'=1.779 gri).
"""
from sinyal_v2.finansal import (FinansalVeri, altman_z2, altman_z_ozel,
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


def test_piotroski_eksik_veri_none():
    tam = _fv(1000, 400, 300, 200, 200, 800, 50, 40, 100)
    eksik = FinansalVeri(
        toplam_aktif=1000, donen_varlik=400, kisa_vadeli_borc=300,
        toplam_borc=500, gecmis_yil_karlari=0, faiz_vergi_oncesi_kar=50,
        satislar=800, net_kar=50)             # CFO/brüt/UVB/hisse yok
    assert piotroski_f(eksik, tam) is None
