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


MODEL_ETIKET = {
    "altman_z2": "Altman Z'' (gelişen piyasa)",
    "altman_z_ozel": "Altman Z' (halka kapalı)",
    "piotroski_f": "Piotroski F (0-9 sağlamlık)",
    "ohlson_o": "Ohlson O (iflas olasılığı)",
    "beneish_m": "Beneish M (manipülasyon)",
    "merton_dd_naive": "Merton DD (halka açık)",
}


def finansal_rapor(sonuclar: list) -> str:
    """Katman B model sonuçlarını (bilimsel değerlendirme) metin olarak render et.

    `sonuclar`: ModelSonucu benzeri (model, skor, bolge, ayrinti) nesneler.
    """
    if not sonuclar:
        return "Bilimsel finansal değerlendirme: veri yok (finansal tablo/piyasa)."
    out = ["BİLİMSEL FİNANSAL DEĞERLENDİRME (Katman B)"]
    for s in sonuclar:
        etiket = MODEL_ETIKET.get(s.model, s.model)
        ek = ""
        if "olasilik" in s.ayrinti:
            ek = f"  (temerrüt olasılığı {s.ayrinti['olasilik']:.1%})"
        elif "temerrut_olasiligi" in s.ayrinti:
            ek = f"  (temerrüt olasılığı {s.ayrinti['temerrut_olasiligi']:.1%})"
        out.append(f"  {etiket:32s} skor={s.skor:>8}  bölge: {s.bolge}{ek}")
    out.append("Not: Katsayılar ABD verisiyle kalibre; BIST için gösterge "
               "amaçlıdır. Yatırım tavsiyesi değildir.")
    return "\n".join(out)


def portfoy_tablosu(satirlar: list[dict]) -> str:
    """Çok firmalı izleme listesini risk skoruna göre sıralı tablo olarak render et.

    Her satır: {hisse, unvan, skor, notu, kritik, yuksek, orta, dusuk, toplam}.
    """
    satirlar = sorted(satirlar, key=lambda r: -r["skor"])
    bas = (f"{'Hisse':<9}{'Not':<4}{'Skor':>6}  {'K':>2}{'Y':>3}{'O':>3}"
           f"{'D':>3}  {'Top':>4}  Şirket")
    cizgi = "─" * 78
    out = ["", "İZLEME LİSTESİ — RİSK SIRALAMASI", cizgi, bas, cizgi]
    for r in satirlar:
        out.append(
            f"{r['hisse']:<9}{r['notu']:<4}{r['skor']:>6.1f}  "
            f"{r['kritik']:>2}{r['yuksek']:>3}{r['orta']:>3}{r['dusuk']:>3}  "
            f"{r['toplam']:>4}  {r['unvan'][:44]}")
    out.append(cizgi)
    out.append("K=Kritik Y=Yüksek O=Orta D=Düşük — Yatırım tavsiyesi değildir.")
    return "\n".join(out)


def portfoy_satiri(hisse: str, unvan: str, skor: SkorAnlik,
                   sinyaller: list[Sinyal]) -> dict:
    """Bir firmanın portföy tablosu satırını (şiddet sayımlı) üret."""
    say = {s: 0 for s in Siddet}
    for sg in sinyaller:
        if not sg.iyilesme:
            say[sg.siddet] += 1
    return {"hisse": hisse, "unvan": unvan, "skor": skor.skor,
            "notu": skor.notu, "kritik": say[Siddet.KRITIK],
            "yuksek": say[Siddet.YUKSEK], "orta": say[Siddet.ORTA],
            "dusuk": say[Siddet.DUSUK],
            "toplam": sum(1 for s in sinyaller if not s.iyilesme)}


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
