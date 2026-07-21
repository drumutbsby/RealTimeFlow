# -*- coding: utf-8 -*-
"""JCR connector testleri — parser (gerçek yapıyı yansıtan fixture) + sinyal yönü.

Parser ayrıca gerçek jcrer.com.tr HTML'ine karşı doğrulandı (10 gerçek kayıt
çıkardı); bu test sentetik fixture ile kararlı regresyon sağlar.
"""
import os
from datetime import datetime

from sinyal_v2.connectors.jcr import (JcrConnector,
                                      derecelendirmeleri_ayristir)
from sinyal_v2.model import KaynakTipi
from sinyal_v2.motor import siniflandir

FIXTURE = os.path.join(os.path.dirname(__file__), "fixtures", "jcr_ornek.html")


def _html():
    with open(FIXTURE, encoding="utf-8") as fh:
        return fh.read()


def test_parser_kayitlari_cikarir():
    kayitlar = derecelendirmeleri_ayristir(_html())
    assert len(kayitlar) == 2                   # başlık/kısa-vade satırları atlandı
    k0 = kayitlar[0]
    assert k0["unvan"] == "ÖRNEK SAĞLAM SANAYİ A.Ş."
    assert k0["yerel_not"] == "BBB (tr)"
    assert k0["yerel_gorunum"] == "Durağan"
    assert k0["tarih"] == "20.07.2026"
    assert k0["sektor"] == "ENERJİ"


def test_connector_cek_ve_saglik():
    c = JcrConnector(http_get=lambda url: _html())
    sonuc = c.cek({})
    assert sonuc.saglik.basarili is True
    assert sonuc.saglik.cekilen_kayit == 2
    assert c.kaynak_tipi is KaynakTipi.DERECELENDIRME


def test_cek_http_get_yoksa_basarisiz():
    sonuc = JcrConnector().cek({})
    assert sonuc.saglik.basarili is False


def test_gorunum_yonu_sinyale_donusur():
    kayitlar = derecelendirmeleri_ayristir(_html())
    c = JcrConnector()
    # Durağan görünüm → risk sinyali DEĞİL
    saglam = next(k for k in kayitlar if "SAĞLAM" in k["unvan"])
    assert siniflandir(c.yuzey_metin(saglam)) is None
    # Negatif görünüm → derecelendirme sinyali
    riskli = next(k for k in kayitlar if "RİSKLİ" in k["unvan"])
    r = siniflandir(c.yuzey_metin(riskli))
    assert r is not None and r.kategori_id == "derecelendirme"


def test_olay_tarihi_ve_ayristir():
    kayitlar = derecelendirmeleri_ayristir(_html())
    c = JcrConnector()
    assert c.olay_tarihi(kayitlar[0]) == datetime(2026, 7, 20)
    kk = c.ayristir(kayitlar[0], firma_id="c1")
    assert kk.kaynak_tipi is KaynakTipi.DERECELENDIRME
    assert kk.id.startswith("jcr:")
    assert kk.firma_id == "c1"
