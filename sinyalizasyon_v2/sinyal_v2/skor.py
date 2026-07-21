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

from .finansal import FinansalVeri, altman_z2, piotroski_f
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


# ── Katman B → risk skoru + Katman A+B fusion (PRD §13.2) ───────────────
# Katman B ağırlıkları V1 regresyonuna dahil DEĞİLDİR (yeni); şeffaf ve
# kalibre edilebilir tutulur. Altman bölgesi → 0-100 finansal risk tabanı.
FINANSAL_BOLGE_RISK = {"sıkıntı": 80.0, "gri": 45.0, "güvenli": 10.0}
FUSION_A_AGIRLIK = 0.55       # olay skoru ağırlığı
FUSION_B_AGIRLIK = 0.45       # finansal skor ağırlığı


def finansal_risk(fv: FinansalVeri,
                  onceki: FinansalVeri | None = None):
    """Finansal tablodan 0-100 finansal risk skoru + açıklama (Katman B).

    None → finansal skor hesaplanamadı (yetersiz veri). Altman Z'' bölgesi
    risk tabanını belirler; Piotroski F (iki dönem varsa) tabanı düzeltir.
    """
    z2 = altman_z2(fv)
    if z2 is None:
        return None
    risk = FINANSAL_BOLGE_RISK[z2.bolge]
    aciklama = [f"Altman Z''={z2.skor} ({z2.bolge}) → finansal risk tabanı "
                f"{risk:.0f}"]
    if onceki is not None:
        f = piotroski_f(fv, onceki)
        if f is not None:
            if f.skor <= 2:
                risk += 10
                aciklama.append(f"Piotroski F={f.skor:.0f} (zayıf) → +10")
            elif f.skor >= 7:
                risk -= 10
                aciklama.append(f"Piotroski F={f.skor:.0f} (güçlü) → −10")
    risk = max(0.0, min(100.0, risk))
    return risk, aciklama


def firma_skoru_hibrit(sinyaller: list[Sinyal],
                       finansal_veri: FinansalVeri | None = None,
                       onceki_finansal: FinansalVeri | None = None,
                       simdi: datetime | None = None) -> SkorAnlik:
    """Katman A (olay) + Katman B (finansal) birleşik skoru (PRD §13.2).

    Finansal veri yoksa Katman A tek başına döner (düşük güven). Varsa iki
    katman güvenilirlik-ağırlıklı birleştirilir ve güven yükselir.
    """
    a_res = firma_skoru(sinyaller, simdi)
    fr = finansal_risk(finansal_veri, onceki_finansal) if finansal_veri else None
    if fr is None:
        return a_res                      # yalnız Katman A

    a = a_res.katman_a
    b, b_aciklama = fr
    fused = min(100.0, round(FUSION_A_AGIRLIK * a + FUSION_B_AGIRLIK * b, 1))
    harf, etiket = not_ver(fused)
    bulgular = [s for s in sinyaller if not s.iyilesme]
    if (bulgular or b >= FINANSAL_BOLGE_RISK["gri"]) and harf == "A":
        harf = "B"

    aciklama = [x for x in a_res.aciklama if "yalnızca olay" not in x]
    aciklama += b_aciklama
    aciklama.append(
        f"fusion: {FUSION_A_AGIRLIK}×Katman A({a:.1f}) + "
        f"{FUSION_B_AGIRLIK}×Katman B({b:.1f}) = {fused:.1f}")
    return SkorAnlik(
        firma_id=a_res.firma_id, tarih=a_res.tarih, skor=fused, notu=harf,
        model_surumu="hibrit_v1", katman_a=a, katman_b=round(b, 1),
        guven=0.85, aciklama=aciklama)
