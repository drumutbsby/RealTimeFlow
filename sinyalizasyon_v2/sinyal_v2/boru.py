# -*- coding: utf-8 -*-
"""Orkestrasyon boru hattı — connector → motor → skor → depo.

Bir firmanın ham kaynak kayıtlarını uçtan uca işler (PRD §14.1 boru hattı):
ayrıştır → kanıt kaydını sakla → sınıflandır → sinyalleri sakla → skorla.
Kaynak-bağımsızdır: herhangi bir `Connector` ile çalışır.
"""
from __future__ import annotations

from datetime import datetime

from .connectors.base import Connector
from .depo import Depo
from .model import Firma, Sinyal, SkorAnlik
from .motor import siniflandir
from .skor import firma_skoru


def firma_isle(depo: Depo, connector: Connector, firma: Firma,
               ham_kayitlar: list[dict], simdi: datetime | None = None
               ) -> SkorAnlik:
    """Bir firmayı verili ham kayıtlarla işle → SkorAnlik (yan etki: depoya yazar).

    Her ham kayıt için: kanıt kaydı saklanır, yüzey metni sınıflandırılır ve
    risk sinyali varsa saklanır. Sonra tüm sinyallerden Katman A skoru üretilir.
    """
    depo.firma_ekle(firma)
    sinyaller: list[Sinyal] = []
    for ham in ham_kayitlar:
        kk = connector.ayristir(ham, firma.canonical_id)
        depo.kaynak_kaydi_ekle(kk)
        sonuc = siniflandir(connector.yuzey_metin(ham))
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
