# -*- coding: utf-8 -*-
"""Bilimsel değerlendirme cephesi testleri — tum_modeller + finansal_rapor."""
from sinyal_v2.finansal import BeneishGirdi, FinansalVeri, tum_modeller
from sinyal_v2.rapor import finansal_rapor

FV = FinansalVeri(
    toplam_aktif=1000, donen_varlik=500, kisa_vadeli_borc=300, toplam_borc=600,
    gecmis_yil_karlari=100, faiz_vergi_oncesi_kar=120, satislar=900, net_kar=80)


def test_tum_modeller_sadece_altman():
    # yalnız tek dönem FV → Altman Z'' ve Z' çalışır (Piotroski/Ohlson için
    # iki dönem gerekir)
    sonuclar = tum_modeller(fv=FV)
    modeller = {s.model for s in sonuclar}
    assert modeller == {"altman_z2", "altman_z_ozel"}


def test_tum_modeller_merton_ve_beneish_eklenir():
    b = BeneishGirdi(satislar=1000, satis_maliyeti=600, ticari_alacaklar=200,
                     donen_varlik=500, maddi_duran_varlik=300, toplam_aktif=1000,
                     amortisman=50, faaliyet_giderleri=100, toplam_borc=400,
                     net_kar=100, faaliyet_nakit_akisi=100)
    sonuclar = tum_modeller(fv=FV, beneish=b, beneish_onceki=b,
                            merton_ozkaynak=1000, merton_vol=0.4,
                            merton_borc=500)
    modeller = {s.model for s in sonuclar}
    assert "beneish_m" in modeller and "merton_dd_naive" in modeller
    assert "altman_z2" in modeller


def test_tum_modeller_veri_yok_bos():
    assert tum_modeller() == []


def test_finansal_rapor_render():
    sonuclar = tum_modeller(fv=FV)
    metin = finansal_rapor(sonuclar)
    assert "BİLİMSEL FİNANSAL DEĞERLENDİRME" in metin
    assert "Altman" in metin
    assert finansal_rapor([]).startswith("Bilimsel finansal değerlendirme: veri yok")
