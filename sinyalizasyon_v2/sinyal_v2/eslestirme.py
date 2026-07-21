# -*- coding: utf-8 -*-
"""Kimlik eşleştirme (entity resolution) — V2'nin en kritik yeni bileşeni.

Farklı kaynaklardaki (KAP, ilan.gov.tr, Ticaret Sicil…) firma kayıtlarını tek
kanonik `Firma`'ya bağlar. PRD §11 ile uyumlu anahtar önceliği:

  1. VKN (kesin)                → güven 1.0
  2. MERSİS'ten çıkarılan VKN   → güven 1.0
  3. Bulanık unvan benzerliği   → güven = benzerlik oranı

Yanlış birleştirme = yanlış sinyal olduğundan, eşik altı bulanık eşleşmeler
sessizce birleştirilmez; `dogrulama_gerekli=True` ile doğrulama kuyruğuna
düşer (PRD §11.4).
"""
from __future__ import annotations

from dataclasses import dataclass
from difflib import SequenceMatcher

from .model import Firma
from .normalize import mersis_icinden_vkn, unvan_anahtari, vkn_normalize

# Bulanık unvan eşleşme eşikleri (unvan_anahtari üzerinden benzerlik oranı)
OTOMATIK_ESIK = 0.92     # ≥ → otomatik birleştir
DOGRULAMA_ESIK = 0.80    # [eşik, OTOMATIK) → doğrulama kuyruğu; altı → eşleşme yok


@dataclass
class EslestirmeSonucu:
    firma_id: str | None       # None → yeni firma (hiç eşleşme yok)
    guven: float               # 0-1
    yontem: str                # "vkn" | "mersis_vkn" | "unvan" | "yok"
    dogrulama_gerekli: bool = False


class Eslestirici:
    """Bilinen firmalar üzerinde kimlik eşleştirmesi yapar."""

    def __init__(self, firmalar: list[Firma] | None = None):
        self._vkn_idx: dict[str, str] = {}          # vkn → canonical_id
        self._unvan_idx: list[tuple[str, str]] = []  # (unvan_anahtari, id)
        for f in firmalar or []:
            self.ekle(f)

    def ekle(self, firma: Firma) -> None:
        """İndekse bir kanonik firma ekle."""
        v = vkn_normalize(firma.vkn) if firma.vkn else None
        if v:
            self._vkn_idx[v] = firma.canonical_id
        # MERSİS'ten de VKN türetip indeksle (kaynak VKN vermese de yakalanır)
        if firma.mersis:
            mv = mersis_icinden_vkn(firma.mersis)
            if mv:
                self._vkn_idx.setdefault(mv, firma.canonical_id)
        anahtar = unvan_anahtari(firma.unvan)
        if anahtar:
            self._unvan_idx.append((anahtar, firma.canonical_id))

    def eslestir(self, vkn: str | None = None, mersis: str | None = None,
                 unvan: str | None = None) -> EslestirmeSonucu:
        """Bir ham kaydı kanonik firmaya eşleştir (öncelik: VKN > MERSİS > unvan)."""
        # 1) Kesin VKN
        v = vkn_normalize(vkn) if vkn else None
        if v and v in self._vkn_idx:
            return EslestirmeSonucu(self._vkn_idx[v], 1.0, "vkn")
        # 2) MERSİS'ten VKN
        if mersis:
            mv = mersis_icinden_vkn(mersis)
            if mv and mv in self._vkn_idx:
                return EslestirmeSonucu(self._vkn_idx[mv], 1.0, "mersis_vkn")
        # 3) Bulanık unvan
        if unvan:
            anahtar = unvan_anahtari(unvan)
            en_iyi_id, en_iyi_oran = None, 0.0
            for aday_anahtar, aday_id in self._unvan_idx:
                oran = SequenceMatcher(None, anahtar, aday_anahtar).ratio()
                if oran > en_iyi_oran:
                    en_iyi_id, en_iyi_oran = aday_id, oran
            if en_iyi_id is not None and en_iyi_oran >= DOGRULAMA_ESIK:
                return EslestirmeSonucu(
                    en_iyi_id, round(en_iyi_oran, 3), "unvan",
                    dogrulama_gerekli=en_iyi_oran < OTOMATIK_ESIK)
        # 4) Eşleşme yok → yeni firma
        return EslestirmeSonucu(None, 0.0, "yok")
