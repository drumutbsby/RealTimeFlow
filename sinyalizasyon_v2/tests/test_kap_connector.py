# -*- coding: utf-8 -*-
"""KAP connector testleri — JSON REST (byCriteria) çekim + legacy flight parser.

byCriteria istek gövdesi ve yanıt işleme, canlı KAP endpoint'ine karşı ayrıca
doğrulandı (gerçek SASA bildirimleri döndü).
"""
import json

from sinyal_v2.connectors.kap import (KapConnector, bycriteria_govde,
                                      flight_dizisi_cikar)
from sinyal_v2.model import KaynakTipi

# byCriteria'nın döndürdüğü JSON dizisini taklit eden sentetik yanıt
SENTETIK_JSON = json.dumps([
    {"disclosureIndex": 123, "subject": "Özel Durum Açıklaması",
     "summary": "İflas Kararı Alınması", "publishDate": "01.05.2026 10:00:00"},
    {"disclosureIndex": 124, "subject": "Finansal Rapor",
     "summary": "2025 raporu", "publishDate": "02.05.2026 09:00:00"},
], ensure_ascii=False)

# Eski gömülü flight-payload (legacy parser regresyonu)
SENTETIK_FLIGHT = (
    'ust ...\\"data\\":['
    '{\\"disclosureBasic\\":{\\"disclosureIndex\\":9,\\"title\\":\\"X\\"}}'
    '] alt'
)


def test_bycriteria_govde_oid_ve_tarih():
    g = bycriteria_govde("OID1", "2025-01-01", "2025-12-31")
    assert g["mkkMemberOidList"] == ["OID1"]
    assert g["fromDate"] == "2025-01-01" and g["toDate"] == "2025-12-31"


def test_cek_http_post_yoksa_sessizce_basari_taklidi_yapmaz():
    sonuc = KapConnector().cek({"oid": "x"})
    assert sonuc.saglik.basarili is False
    assert "http_post" in (sonuc.saglik.hata or "")


def test_cek_json_rest_ayristirir():
    c = KapConnector(http_post=lambda url, govde: SENTETIK_JSON)
    sonuc = c.cek({"oid": "x", "bas_tarih": "2026-01-01",
                   "bit_tarih": "2026-12-31"})
    assert sonuc.saglik.basarili is True
    assert sonuc.saglik.cekilen_kayit == 2
    assert sonuc.ham_kayitlar[0]["disclosureIndex"] == 123


def test_cek_ag_hatasi_basarisiz_saglik():
    def patlat(url, govde):
        raise RuntimeError("ağ hatası")
    sonuc = KapConnector(http_post=patlat).cek({"oid": "x"})
    assert sonuc.saglik.basarili is False
    assert "ağ hatası" in (sonuc.saglik.hata or "")


def test_ayristir_ve_yuzey_metin():
    c = KapConnector()
    kk = c.ayristir({"disclosureIndex": 999, "subject": "X"}, firma_id="c1")
    assert kk.id == "kap:999" and kk.kaynak_tipi is KaynakTipi.KAP
    assert kk.kaynak_url.endswith("/tr/Bildirim/999")
    # KAP JSON kaydından yüzey metni (subject+summary) üretilir
    metin = c.yuzey_metin({"subject": "Özel Durum", "summary": "İflas Kararı"})
    assert "İflas" in metin


# ── legacy flight parser (geriye dönük) ──
def test_flight_ayristir_temel():
    arr = flight_dizisi_cikar(SENTETIK_FLIGHT)
    assert isinstance(arr, list) and arr[0]["disclosureBasic"]["disclosureIndex"] == 9


def test_flight_anchor_yok_none():
    assert flight_dizisi_cikar("veri blogu yok") is None
