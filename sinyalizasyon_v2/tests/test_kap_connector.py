# -*- coding: utf-8 -*-
"""KAP connector testleri — saf flight-payload ayrıştırıcı + sağlık davranışı."""
from sinyal_v2.connectors.kap import KapConnector, flight_dizisi_cikar
from sinyal_v2.model import KaynakTipi

# Gerçek KAP sayfasındaki escape'li gömülü diziyi taklit eden sentetik yük.
# Python kaynağında \\" → çalışma zamanında \"  (yani KAP'ın kaçışlı biçimi).
SENTETIK_SAYFA = (
    'ust bilgi ...\\"data\\":['
    '{\\"disclosureBasic\\":{\\"disclosureIndex\\":123,'
    '\\"title\\":\\"Ozel Durum Aciklamasi\\"}},'
    '{\\"disclosureBasic\\":{\\"disclosureIndex\\":124,'
    '\\"title\\":\\"Finansal Rapor\\"}}'
    '] alt bilgi'
)


def test_flight_ayristir_temel():
    arr = flight_dizisi_cikar(SENTETIK_SAYFA)
    assert isinstance(arr, list) and len(arr) == 2
    assert arr[0]["disclosureBasic"]["disclosureIndex"] == 123


def test_flight_anchor_yok_none():
    # Veri bloğu hiç yoksa None döner ("temiz firma" DEĞİL → yeniden deneme)
    assert flight_dizisi_cikar("hicbir veri blogu yok") is None


def test_cek_http_get_yoksa_sessizce_basari_taklidi_yapmaz():
    c = KapConnector(http_get=None)
    sonuc = c.cek({"oid": "abc"})
    assert sonuc.saglik.basarili is False       # sessiz veri kaybı yasak
    assert sonuc.ham_kayitlar == []
    assert "http_get" in (sonuc.saglik.hata or "")


def test_cek_enjekte_edilen_http_get_ile_ayristirir():
    c = KapConnector(http_get=lambda url: SENTETIK_SAYFA)
    sonuc = c.cek({"oid": "abc", "yil": 2025})
    assert sonuc.saglik.basarili is True
    assert sonuc.saglik.cekilen_kayit == 2
    assert sonuc.ham_kayitlar[1]["disclosureIndex"] == 124


def test_cek_ag_hatasi_basarisiz_saglik():
    def patlat(url):
        raise RuntimeError("ağ hatası")
    c = KapConnector(http_get=patlat)
    sonuc = c.cek({"oid": "abc"})
    assert sonuc.saglik.basarili is False
    assert "ağ hatası" in (sonuc.saglik.hata or "")


def test_ayristir_kaynak_kaydi_uretir():
    c = KapConnector()
    kk = c.ayristir({"disclosureIndex": 999, "title": "X"}, firma_id="c1")
    assert kk.id == "kap:999"
    assert kk.firma_id == "c1"
    assert kk.kaynak_tipi is KaynakTipi.KAP
    assert kk.kaynak_url.endswith("/tr/Bildirim/999")
