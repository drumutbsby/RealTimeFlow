# -*- coding: utf-8 -*-
"""Skorlama motoru — Katman A (olay/sinyal skoru), V1'den taşındı.

PRD §13.1: nihai skor iki katmanlıdır. Bu modül **Katman A**'yı (kamuya açık
olaylardan gelen ağırlıklı, güncellik çarpanlı, kategori-içi sönümlemeli skor)
uygular; deterministik ve açıklanabilir. **Katman B** (Altman/Ohlson/Merton)
finansal veri gerektirir ve ileriki fazda eklenir — yokken skor açıkça "yalnızca
olay verisine dayanıyor" olarak işaretlenir.

Skor ağırlıkları V1 ile aynıdır ve gerekçesiz değiştirilmez (regresyon).
"""
from __future__ import annotations

from datetime import datetime

from .model import SkorAnlik, Sinyal

# V1 skorlama sabitleri (aynen)
RECENCY_STEPS = [(90, 1.0), (365, 0.75), (730, 0.5)]
RECENCY_FLOOR = 0.3
SCORE_GAIN = 2.4          # bulgu ağırlığı → skor katkısı çarpanı
TEKRAR_SONUMLEME = 0.35   # aynı kategorideki 2. ve sonraki bulgular

# (eşik, harf, etiket) — skor >= eşik ilk eşleşen
GRADE_META = [
    (70, "E", "KRİTİK"),
    (45, "D", "YÜKSEK"),
    (20, "C", "ORTA"),
    (1,  "B", "DÜŞÜK"),
    (0,  "A", "TEMİZ"),
]

MODEL_SURUMU = "katman_a_v1"


def guncellik_faktoru(tarih: datetime, simdi: datetime | None = None) -> float:
    """Bulgunun yaşına göre güncellik çarpanı (yeni olay = ağır)."""
    if tarih == datetime.min:
        return RECENCY_FLOOR
    simdi = simdi or datetime.now()
    yas = (simdi - tarih).days
    for sinir, faktor in RECENCY_STEPS:
        if yas <= sinir:
            return faktor
    return RECENCY_FLOOR


def not_ver(skor: float) -> tuple[str, str]:
    """Skoru A–E notuna çevir → (harf, etiket)."""
    for esik, harf, etiket in GRADE_META:
        if skor >= esik:
            return harf, etiket
    return GRADE_META[-1][1], GRADE_META[-1][2]


def firma_skoru(sinyaller: list[Sinyal], simdi: datetime | None = None,
                model_surumu: str = MODEL_SURUMU) -> SkorAnlik:
    """Bir firmanın sinyallerinden Katman A skoru + açıklama üret.

    İyileşme sinyalleri skora KATILMAZ (V1). Aynı kategorideki tekrar bulgular
    azalan ağırlıkla sayılır (tek olay birden çok bildirim doğurabilir → şişme
    önlenir).
    """
    simdi = simdi or datetime.now()
    bulgular = [s for s in sinyaller if not s.iyilesme]

    by_cat: dict[str, list[tuple[float, Sinyal]]] = {}
    for s in bulgular:
        g = guncellik_faktoru(s.tarih, simdi)
        by_cat.setdefault(s.kategori_id, []).append((g, s))

    skor = 0.0
    aciklama: list[str] = []
    for cat_id, liste in by_cat.items():
        liste.sort(key=lambda gs: -(gs[1].agirlik * gs[0]))
        cat_katki = 0.0
        for rank, (g, s) in enumerate(liste):
            damp = 1.0 if rank == 0 else TEKRAR_SONUMLEME
            cat_katki += s.agirlik * g * SCORE_GAIN * damp
        skor += cat_katki
        aciklama.append(
            f"{liste[0][1].kategori}: +{cat_katki:.1f} puan ({len(liste)} bulgu)")
    skor = min(100.0, skor)
    aciklama.sort(key=lambda x: -float(x.split("+")[1].split(" ")[0]))

    harf, etiket = not_ver(skor)
    if bulgular and harf == "A":
        harf, etiket = "B", "DÜŞÜK"      # bulgusu olan asla "TEMİZ" olmaz

    # Katman B yok → güven düşük (yalnız olay verisi). Bulgu yoksa temiz/yüksek güven.
    if not bulgular:
        guven = 1.0
    else:
        guven = 0.6
        aciklama.append("skor yalnızca olay verisine dayanıyor "
                        "(finansal model katmanı yok)")

    return SkorAnlik(
        firma_id=bulgular[0].firma_id if bulgular else "",
        tarih=simdi, skor=round(skor, 1), notu=harf, model_surumu=model_surumu,
        katman_a=round(skor, 1), katman_b=None, guven=guven, aciklama=aciklama)
