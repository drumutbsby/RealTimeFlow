# -*- coding: utf-8 -*-
"""eslestirme.py birim testleri — kimlik eşleştirme (entity resolution)."""
from sinyal_v2.eslestirme import OTOMATIK_ESIK, Eslestirici
from sinyal_v2.model import Firma


def _eslestirici():
    return Eslestirici([
        Firma(canonical_id="c-thy", unvan="Türk Hava Yolları A.O.",
              vkn="8760047464"),
        Firma(canonical_id="c-gar", unvan="T. Garanti Bankası A.Ş.",
              mersis="0879001756600379"),        # vkn yok, MERSİS'ten türetilir
        Firma(canonical_id="c-sasa", unvan="SASA POLYESTER SANAYİ A.Ş."),
    ])


def test_kesin_vkn_eslesmesi():
    r = _eslestirici().eslestir(vkn="8760047464")
    assert r.firma_id == "c-thy" and r.guven == 1.0 and r.yontem == "vkn"
    assert r.dogrulama_gerekli is False


def test_mersisten_vkn_eslesmesi():
    e = _eslestirici()
    r = e.eslestir(mersis="0879001756600379")
    assert r.firma_id == "c-gar" and r.yontem == "mersis_vkn" and r.guven == 1.0
    # MERSİS'ten türetilen VKN, doğrudan VKN sorgusuyla da yakalanır
    r2 = e.eslestir(vkn="8790017566")
    assert r2.firma_id == "c-gar" and r2.yontem == "vkn"


def test_bilinmeyen_vkn_eslesme_yok():
    # geçerli ama indekste olmayan VKN → yeni firma
    r = _eslestirici().eslestir(vkn="2120133627")
    assert r.firma_id is None and r.yontem == "yok"


def test_bulanik_unvan_otomatik():
    r = _eslestirici().eslestir(unvan="SASA POLYESTER SANAYİ ANONİM ŞİRKETİ")
    assert r.firma_id == "c-sasa" and r.yontem == "unvan"
    assert r.guven >= OTOMATIK_ESIK and r.dogrulama_gerekli is False


def test_bulanik_unvan_dogrulama_kuyrugu():
    # kısmi benzerlik → sessizce birleştirilmez, doğrulama gerekli
    r = _eslestirici().eslestir(unvan="SASA POLYESTER KİMYA")
    assert r.firma_id == "c-sasa" and r.dogrulama_gerekli is True


def test_alakasiz_unvan_eslesme_yok():
    r = _eslestirici().eslestir(unvan="Bambaşka Bir Firma Ltd.")
    assert r.firma_id is None and r.yontem == "yok"
