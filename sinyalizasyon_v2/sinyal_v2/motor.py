# -*- coding: utf-8 -*-
"""Sinyal sınıflandırma motoru — kaynak-bağımsız (V1 `classify` çekirdeği).

Bir kaynaktan gelen serbest metni (başlık/özet/konu ve varsa derin tam metin)
alır, V1'in kanıtlanmış kurallarıyla sınıflandırır ve bir `SinyalSonucu` döner
(veya risk yoksa None). KAP'a özgü değildir; her connector'ın normalize ettiği
metne uygulanır.

V1'den bilinçli AYRIM: KAP'a özgü türetilmiş sinyaller (finansal rapor gecikmesi
tarih aritmetiği) ve BIST/SPK piyasa-geneli yayıncı ayrımı burada DEĞİL, ilgili
connector'ın zenginleştirme adımındadır (kaynak-özgü bağlam gerektirir).
"""
from __future__ import annotations

from dataclasses import dataclass

from .kurallar import (IMPROVEMENT_HINTS_BY_CAT, NOISE_PATTERNS, RATING_NEGATIVE,
                       RATING_POSITIVE, RATING_TRIGGERS, RISK_CATEGORIES,
                       RISK_RULES)
from .model import Siddet
from .normalize import norm


@dataclass
class SinyalSonucu:
    """Sınıflandırma çıktısı. Firma/kaynak bağlaması YOK — pipeline ekler."""
    kategori_id: str
    kategori: str
    siddet: Siddet
    agirlik: int
    gerekce: str
    iyilesme: bool = False


def _sonuc(cat_id: str, siddet: Siddet, agirlik: int, gerekce: str,
           iyilesme: bool = False) -> SinyalSonucu:
    return SinyalSonucu(cat_id, RISK_CATEGORIES[cat_id][0], siddet, agirlik,
                        gerekce, iyilesme)


def siniflandir(yuzey_metin: str, derin_metin: str = "") -> SinyalSonucu | None:
    """Tek bir kaynak metnini sınıflandır. None → risk sinyali değil."""
    text = norm(yuzey_metin)
    deep = norm(derin_metin) if derin_metin else ""
    combined = text + " ~ " + deep
    if not text.strip():
        return None
    for noise in NOISE_PATTERNS:
        if noise in text:
            return None

    # 1) Derecelendirme: yön analizi (başlık/özet VE derin metin birlikte)
    if any(k in text for k in RATING_TRIGGERS):
        probe = combined
        neg = [k for k in RATING_NEGATIVE if k in probe]
        pos = [k for k in RATING_POSITIVE if k in probe]
        if neg and (not pos or len(neg) >= len(pos)):
            return _sonuc("derecelendirme", Siddet.KRITIK, 9,
                          f"olumsuz not aksiyonu tespit edildi "
                          f"({', '.join(neg[:3])})")
        if pos and not neg:
            return None                      # teyit / yükseltme → risk değil
        if deep:
            return None                      # detay okundu, olumsuzluk yok
        return _sonuc("derecelendirme", Siddet.DUSUK, 3,
                      "derecelendirme bildirimi — yön özetten belirlenemedi "
                      "(rutin yıllık not yayını olabilir), derin analiz önerilir")

    # 2) Genel kurallar (önce yüzey metni, derin metin de aranır)
    for cat_id, keywords in RISK_RULES:
        _, weight = RISK_CATEGORIES[cat_id]
        for kw in keywords:
            hit_surface = kw in text
            hit_deep = bool(deep) and kw in deep
            if not (hit_surface or hit_deep):
                continue
            # iyileşme yalnızca EŞLEŞEN kategorinin kendi kalıplarıyla
            cat_hints = IMPROVEMENT_HINTS_BY_CAT.get(cat_id, ())
            if any(h in combined for h in cat_hints):
                return _sonuc(cat_id, Siddet.DUSUK, 0,
                              f"olumlu yönlü gelişme ('{kw}' bağlamında "
                              "kaldırma/çıkarma/lehte sonuç ifadesi)",
                              iyilesme=True)
            w = weight if hit_surface else max(1, weight - 1)
            src = "başlık/özet" if hit_surface else "tam metin"
            return _sonuc(cat_id, Siddet.agirliktan(w), w,
                          f"'{kw}' ifadesi ({src})")
    return None
