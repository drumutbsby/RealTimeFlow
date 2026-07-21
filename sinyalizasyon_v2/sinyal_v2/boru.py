# -*- coding: utf-8 -*-
"""Orkestrasyon boru hattı — connector → motor → skor → depo.

Bir firmanın ham kaynak kayıtlarını uçtan uca işler (PRD §14.1 boru hattı):
ayrıştır → kanıt kaydını sakla → sınıflandır → sinyalleri sakla → skorla.
Kaynak-bağımsızdır: herhangi bir `Connector` ile çalışır.
"""
from __future__ import annotations

import re
from datetime import datetime

from .connectors.base import Connector
from .depo import Depo
from .eslestirme import Eslestirici
from .model import Firma, Sinyal, SkorAnlik
from .motor import siniflandir
from .normalize import norm
from .skor import firma_skoru


def firma_isle(depo: Depo, connector: Connector, firma: Firma,
               ham_kayitlar: list[dict], simdi: datetime | None = None,
               detay_getir=None, derin_limit: int = 40) -> SkorAnlik:
    """Bir firmayı verili ham kayıtlarla işle → SkorAnlik (yan etki: depoya yazar).

    Her ham kayıt için: kanıt kaydı saklanır, yüzey metni sınıflandırılır ve
    risk sinyali varsa saklanır. Sonra tüm sinyallerden Katman A skoru üretilir.

    `detay_getir(ham) -> str` verilirse, YÖNÜ belirsiz derecelendirme bildirimleri
    için detay metni çekilip yeniden sınıflandırılır (derin mod); en fazla
    `derin_limit` kayıt (kaynağa saygı).
    """
    depo.firma_ekle(firma)
    sinyaller: list[Sinyal] = []
    derin_sayac = 0
    for ham in ham_kayitlar:
        kk = connector.ayristir(ham, firma.canonical_id)
        depo.kaynak_kaydi_ekle(kk)
        sonuc = siniflandir(connector.yuzey_metin(ham))
        # Derin mod: yönü özetten belirlenemeyen derecelendirme (ağırlık ≤3) →
        # detay metnini oku, yeniden sınıflandır (düşürme/teyit netleşsin)
        if (detay_getir is not None and derin_sayac < derin_limit
                and sonuc is not None and sonuc.kategori_id == "derecelendirme"
                and sonuc.agirlik <= 3):
            derin = detay_getir(ham)
            if derin:
                derin_sayac += 1
                sonuc = siniflandir(connector.yuzey_metin(ham), derin) or sonuc
        if sonuc is None:
            continue
        s = Sinyal(
            firma_id=firma.canonical_id, kategori_id=sonuc.kategori_id,
            kategori=sonuc.kategori, siddet=sonuc.siddet, agirlik=sonuc.agirlik,
            tarih=connector.olay_tarihi(ham), kaynak_kaydi_id=kk.id,
            kaynak_tipi=connector.kaynak_tipi, gerekce=sonuc.gerekce,
            kaynak_url=kk.kaynak_url, iyilesme=sonuc.iyilesme)
        depo.sinyal_ekle(s)
        sinyaller.append(s)
    skor = firma_skoru(sinyaller, simdi)
    skor.firma_id = firma.canonical_id      # bulgu olmasa da firma kimliği kalsın
    return skor


def _yeni_firma_id(unvan: str) -> str:
    slug = re.sub(r"\W+", "-", norm(unvan)).strip("-")[:40] or "bilinmeyen"
    return f"auto-{slug}"


def kaynak_tarama(depo: Depo, eslestirici: Eslestirici, connector: Connector,
                  ham_kayitlar: list[dict], simdi: datetime | None = None
                  ) -> dict[str, SkorAnlik]:
    """Kaynak-güdümlü keşif: her kayıt bir firma adlandırır.

    Kaydı kanonik firmaya çözer (yoksa oluşturup indeksler), kanıtı ve sinyali
    saklar, sonra firma başına Katman A skoru üretir. → {firma_id: SkorAnlik}.
    Bir firmanın kimliği bilinmiyorsa sessizce atlanmaz; unvandan kanonik kayıt
    türetilir (kimlik eşleştirme ileride VKN/MERSİS ile zenginleşir).
    """
    firma_sinyalleri: dict[str, list[Sinyal]] = {}
    for ham in ham_kayitlar:
        kimlik = connector.firma_kimligi(ham)
        unvan = (kimlik.get("unvan") or "").strip()
        if not unvan:
            continue                         # kimliksiz kayıt işlenemez (atla)
        es = eslestirici.eslestir(vkn=kimlik.get("vkn"),
                                  mersis=kimlik.get("mersis"), unvan=unvan)
        if es.firma_id is None:
            firma = Firma(canonical_id=_yeni_firma_id(unvan), unvan=unvan,
                          vkn=kimlik.get("vkn"), mersis=kimlik.get("mersis"))
            depo.firma_ekle(firma)
            eslestirici.ekle(firma)
            fid = firma.canonical_id
        else:
            fid = es.firma_id
        kk = connector.ayristir(ham, fid)
        depo.kaynak_kaydi_ekle(kk)
        firma_sinyalleri.setdefault(fid, [])
        sonuc = siniflandir(connector.yuzey_metin(ham))
        if sonuc is not None:
            s = Sinyal(
                firma_id=fid, kategori_id=sonuc.kategori_id,
                kategori=sonuc.kategori, siddet=sonuc.siddet,
                agirlik=sonuc.agirlik, tarih=connector.olay_tarihi(ham),
                kaynak_kaydi_id=kk.id, kaynak_tipi=connector.kaynak_tipi,
                gerekce=sonuc.gerekce, kaynak_url=kk.kaynak_url,
                iyilesme=sonuc.iyilesme)
            depo.sinyal_ekle(s)
            firma_sinyalleri[fid].append(s)

    sonuclar: dict[str, SkorAnlik] = {}
    for fid, sinyaller in firma_sinyalleri.items():
        sk = firma_skoru(sinyaller, simdi)
        sk.firma_id = fid
        sonuclar[fid] = sk
    return sonuclar
