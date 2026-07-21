# -*- coding: utf-8 -*-
"""Rapor render — firma dosyasını metin ve CSV olarak biçimlendirir.

Saf fonksiyonlar (yan etkisiz), böylece hem CLI hem ileride UI aynı çıktıyı
üretebilir. Her sinyal kaynağına (link) bağlıdır → kanıt zinciri korunur.
"""
from __future__ import annotations

import csv
import io
from datetime import datetime

from .model import Firma, Siddet, Sinyal, SkorAnlik

SIDDET_EMOJI = {
    Siddet.KRITIK: "🔴", Siddet.YUKSEK: "🟠",
    Siddet.ORTA: "🟡", Siddet.DUSUK: "🔵",
}


def _tarih_str(dt: datetime, bicim: str = "%d.%m.%Y") -> str:
    return dt.strftime(bicim) if dt != datetime.min else "-"


def firma_raporu_metin(firma: Firma, skor: SkorAnlik,
                       sinyaller: list[Sinyal]) -> str:
    """Bir firmanın 360° metin dosyasını üret."""
    satir: list[str] = []
    satir.append(f"═══ {firma.unvan} ═══")
    kimlik = firma.vkn or firma.mersis or firma.canonical_id
    satir.append(f"Kimlik: {kimlik}  |  Skor: {skor.skor:.1f}/100  "
                 f"Not: {skor.notu}  |  Güven: {skor.guven:.0%}")
    if skor.aciklama:
        satir.append("Katkı dökümü:")
        satir += [f"  • {a}" for a in skor.aciklama]

    aktif = [s for s in sinyaller if not s.iyilesme]
    iyilesme = [s for s in sinyaller if s.iyilesme]
    if aktif:
        satir.append(f"Risk sinyalleri ({len(aktif)}):")
        for s in sorted(aktif, key=lambda s: (int(s.siddet),
                                              -s.tarih.timestamp()
                                              if s.tarih != datetime.min else 0)):
            emoji = SIDDET_EMOJI.get(s.siddet, "")
            satir.append(f"  {emoji} [{s.siddet.etiket:^6}] {_tarih_str(s.tarih)} "
                         f"{s.kategori} — {s.gerekce}")
    else:
        satir.append("Risk sinyali yok.")
    if iyilesme:
        satir.append(f"İyileşme sinyalleri ({len(iyilesme)}):")
        satir += [f"  ↗ {s.kategori} — {s.gerekce}" for s in iyilesme]
    satir.append("Not: Yatırım tavsiyesi değildir; veriler kamuya açık "
                 "kaynaklardan derlenir, karar öncesi asılları doğrulayınız.")
    return "\n".join(satir)


def sinyaller_csv(sinyaller: list[Sinyal]) -> str:
    """Sinyalleri CSV metnine dök (Excel-uyumlu)."""
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["firma_id", "tarih", "siddet", "kategori", "agirlik",
                "gerekce", "iyilesme", "kaynak_url"])
    for s in sinyaller:
        w.writerow([s.firma_id, _tarih_str(s.tarih, "%d.%m.%Y %H:%M"),
                    s.siddet.etiket, s.kategori, s.agirlik, s.gerekce,
                    "evet" if s.iyilesme else "hayır", s.kaynak_url])
    return buf.getvalue()
