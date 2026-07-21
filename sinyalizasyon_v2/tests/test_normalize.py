# -*- coding: utf-8 -*-
"""normalize.py birim testleri."""
from sinyal_v2 import normalize as nz


def test_norm_tr_karakter_ve_kesme():
    assert nz.norm("İFLAS") == "iflas"
    assert nz.norm("Şirket’in") == "sirketin"
    assert nz.norm("ÇĞÖÜ") == "cgou"
    assert nz.norm("") == ""


def test_unvan_anahtari_ekleri_temizler():
    assert nz.unvan_anahtari("SASA POLYESTER SANAYİ A.Ş.") == "sasa polyester"
    assert nz.unvan_anahtari("KONTROLMATİK TEKNOLOJİ A.Ş.") == "kontrolmatik teknoloji"
    # ek yoksa olduğu gibi (sadeleştirilmiş)
    assert nz.unvan_anahtari("MARTI OTEL") == "marti otel"


def test_vkn_yapisal_red():
    assert not nz.vkn_gecerli("123")            # kısa
    assert not nz.vkn_gecerli("12345678901")    # uzun
    assert not nz.vkn_gecerli("abcdefghij")     # rakam değil
    assert not nz.vkn_gecerli("")
    assert nz.vkn_normalize("123") is None


# Bilinen GERÇEK ve GEÇERLİ VKN'ler — checksum'ı bağımsızca doğrulanmıştır
# (kamuya açık kayıtlar; araştırma ajanı teyidi, bkz. PRD doğrulama akışı).
GECERLI_VKN = {
    "8760047464": "Türk Hava Yolları A.O.",
    "8760578179": "THY Teknik A.Ş.",
    "5700020575": "Koç Holding A.Ş.",
    "8790017566": "T. Garanti Bankası A.Ş.",
    "2120133627": "Turkcell Ödeme A.Ş.",
}
# Checksum'ı TUTMAYAN (son hanesi yanlış) negatif vakalar
GECERSIZ_VKN = ["4840847948", "0810004856"]


def test_vkn_bilinen_gercek_ornekler():
    for vkn, kim in GECERLI_VKN.items():
        assert nz.vkn_gecerli(vkn), f"{vkn} ({kim}) geçerli olmalı"
        assert nz.vkn_normalize(vkn) == vkn
    for vkn in GECERSIZ_VKN:
        assert not nz.vkn_gecerli(vkn), f"{vkn} reddedilmeli"


def test_vkn_checksum_ic_tutarlilik():
    # Bir 9-haneli önek için TAM BİR geçerli kontrol hanesi olmalı.
    # (Algoritmanın GİB spesifikasyonuyla doğruluğu ayrıca ajanla teyit edilir;
    #  bu test regresyona ve iç tutarlılığa karşı korur.)
    for onek in ("123456789", "111111111", "480123456"):
        gecerliler = [d for d in range(10) if nz.vkn_gecerli(onek + str(d))]
        assert len(gecerliler) == 1, (onek, gecerliler)
        tam = onek + str(gecerliler[0])
        assert nz.vkn_normalize(tam) == tam


def test_mersis_yapisal():
    assert nz.mersis_gecerli("0" * 16)
    assert not nz.mersis_gecerli("0" * 15)
    assert nz.mersis_normalize("1234-5678-9012-3456") == "1234567890123456"
    assert nz.mersis_normalize("123") is None


def test_mersis_icinden_vkn():
    # Garanti Bankası MERSİS'i → gömülü VKN (ajan doğrulaması)
    assert nz.mersis_icinden_vkn("0879001756600379") == "8790017566"
    # gömülü 10 hane checksum'ı tutmuyorsa None (0484084794800000 → 4840847948)
    assert nz.mersis_icinden_vkn("0484084794800000") is None
    assert nz.mersis_icinden_vkn("123") is None
