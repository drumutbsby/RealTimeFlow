# -*- coding: utf-8 -*-
"""Uçtan uca boru hattı testi — connector → motor → skor → depo."""
from datetime import datetime

from sinyal_v2.boru import firma_isle
from sinyal_v2.connectors.kap import KapConnector
from sinyal_v2.depo import Depo
from sinyal_v2.model import Firma, Siddet

SIMDI = datetime(2026, 6, 1)


def _kap(idx, title, summary, tarih="01.05.2026 10:00:00"):
    return {"disclosureIndex": idx, "title": title, "summary": summary,
            "publishDate": tarih}


def test_uctan_uca_iflas_ve_rutin():
    depo = Depo()
    conn = KapConnector()
    firma = Firma(canonical_id="c1", unvan="Test A.Ş.")
    ham = [
        _kap(1, "Özel Durum Açıklaması", "İflas Kararı Alınması Hakkında"),
        _kap(2, "Pay Dışında Sermaye Piyasası Aracı İşlemleri",
             "TRF ISIN Kodlu Finansman Bonosunun 3. Kupon Ödemesi"),  # rutin→None
    ]
    skor = firma_isle(depo, conn, firma, ham, SIMDI)

    # tek risk sinyali (iflas), rutin kupon elendi
    sinyaller = depo.firma_sinyalleri("c1")
    assert len(sinyaller) == 1
    assert sinyaller[0].kategori_id == "iflas"
    assert sinyaller[0].siddet is Siddet.KRITIK
    assert sinyaller[0].tarih == datetime(2026, 5, 1, 10, 0, 0)

    # her iki ham kayıt da kanıt olarak saklandı
    assert depo.kaynak_kaydi_getir("kap:1") is not None
    assert depo.kaynak_kaydi_getir("kap:2") is not None

    # skor: iflas ağırlık 10, güncellik 1.0 → 24.0 → C
    assert skor.skor == 24.0 and skor.notu == "C"
    assert skor.firma_id == "c1"


def test_derin_derecelendirme_yon_tespiti():
    conn = KapConnector()
    firma = Firma(canonical_id="c1", unvan="X A.Ş.")
    ham = [{"disclosureIndex": 1, "subject": "Kredi Derecelendirmesi",
            "summary": "Kredi Notu"}]
    # Derin mod YOK → yön belirsiz (DÜŞÜK)
    depo0 = Depo()
    firma_isle(depo0, conn, firma, ham, SIMDI)
    s0 = depo0.firma_sinyalleri("c1")
    assert len(s0) == 1 and s0[0].siddet is Siddet.DUSUK
    # Derin mod: detay 'düşürme' metni → KRİTİK
    depo1 = Depo()
    firma_isle(depo1, conn, firma, ham, SIMDI,
               detay_getir=lambda h: "kredi notunu düşürmüştür, görünüm negatif")
    s1 = depo1.firma_sinyalleri("c1")
    assert len(s1) == 1 and s1[0].siddet is Siddet.KRITIK


def test_birebir_tekrar_ayiklanir():
    # aynı kategori + gün + gerekçe (tek olayın iki bildirimi) → tek sinyal
    depo = Depo()
    conn = KapConnector()
    firma = Firma(canonical_id="c1", unvan="X A.Ş.")
    ham = [_kap(1, "Özel Durum", "İflas Kararı", "01.05.2026 10:00:00"),
           _kap(2, "Özel Durum", "İflas Kararı", "01.05.2026 15:00:00")]
    firma_isle(depo, conn, firma, ham, SIMDI)
    assert len(depo.firma_sinyalleri("c1")) == 1


def test_ayni_kategori_farkli_gun_ayri_sinyal():
    depo = Depo()
    conn = KapConnector()
    firma = Firma(canonical_id="c1", unvan="X A.Ş.")
    ham = [_kap(1, "Özel Durum", "İflas Kararı", "01.05.2026 10:00:00"),
           _kap(2, "Özel Durum", "İflas Kararı", "10.05.2026 10:00:00")]
    firma_isle(depo, conn, firma, ham, SIMDI)
    assert len(depo.firma_sinyalleri("c1")) == 2   # farklı gün → ayrı


def test_uctan_uca_temiz_firma():
    depo = Depo()
    conn = KapConnector()
    firma = Firma(canonical_id="c2", unvan="Temiz A.Ş.")
    ham = [_kap(9, "Genel Kurul İşlemlerine İlişkin Bildirim",
                "2025 Yılı Olağan Genel Kurul Toplantısı Daveti")]
    skor = firma_isle(depo, conn, firma, ham, SIMDI)
    assert depo.firma_sinyalleri("c2") == []
    assert skor.skor == 0.0 and skor.notu == "A" and skor.firma_id == "c2"
