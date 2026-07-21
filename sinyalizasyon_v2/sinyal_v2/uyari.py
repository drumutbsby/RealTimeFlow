# -*- coding: utf-8 -*-
"""Erken uyarı / değişim tespiti (PRD §17).

Bir firmanın önceki skor anlık görüntüsü ile yenisini karşılaştırıp uyarı üretir:
not kötüleşmesi, belirgin skor artışı veya izlemeye yüksek riskle giren yeni
firma. V1'in "önceki taramaya göre yeni bulgu" felsefesinin skor-düzeyi evrimi.
"""
from __future__ import annotations

from .model import SkorAnlik

NOT_SIRA = {"A": 0, "B": 1, "C": 2, "D": 3, "E": 4}
SKOR_ARTIS_ESIK = 15.0          # bu kadar/daha fazla artış uyarı üretir
YUKSEK_RISK_NOTU = 3            # D ve üzeri (D=3, E=4)


def _sira(notu: str) -> int:
    return NOT_SIRA.get(notu, 0)


def uyari_uret(onceki: SkorAnlik | None, yeni: SkorAnlik) -> dict | None:
    """İki skor anlık görüntüsünü karşılaştır → uyarı sözlüğü veya None.

    onceki None ise firma izlemeye YENİ girmiştir; yalnızca yüksek riskliyse
    (D/E) uyarı üretilir.
    """
    sebepler: list[str] = []
    if onceki is None:
        if _sira(yeni.notu) >= YUKSEK_RISK_NOTU:
            sebepler.append(f"izlemeye yüksek riskle giren yeni firma "
                            f"({yeni.notu}, {yeni.skor:.1f})")
    else:
        if _sira(yeni.notu) > _sira(onceki.notu):
            sebepler.append(f"risk notu kötüleşti: {onceki.notu} → {yeni.notu}")
        fark = yeni.skor - onceki.skor
        if fark >= SKOR_ARTIS_ESIK:
            sebepler.append(f"risk skoru +{fark:.1f} arttı "
                            f"({onceki.skor:.1f} → {yeni.skor:.1f})")
    if not sebepler:
        return None
    return {"firma_id": yeni.firma_id, "notu": yeni.notu, "skor": yeni.skor,
            "sebepler": sebepler}


def uyarilari_uret(onceki_map: dict[str, SkorAnlik],
                   yeni_map: dict[str, SkorAnlik]) -> list[dict]:
    """Firma haritalarını karşılaştır → uyarı listesi (skora göre sıralı)."""
    uyarilar = []
    for fid, yeni in yeni_map.items():
        u = uyari_uret(onceki_map.get(fid), yeni)
        if u:
            uyarilar.append(u)
    return sorted(uyarilar, key=lambda u: -u["skor"])


def uyari_metni(uyarilar: list[dict]) -> str:
    """Uyarı listesini kullanıcıya dönük metne çevir."""
    if not uyarilar:
        return "Yeni uyarı yok."
    out = [f"⚠️  {len(uyarilar)} UYARI"]
    for u in uyarilar:
        out.append(f"  {u['firma_id']} (skor {u['skor']:.1f}, not {u['notu']}):")
        out += [f"     • {s}" for s in u["sebepler"]]
    return "\n".join(out)
