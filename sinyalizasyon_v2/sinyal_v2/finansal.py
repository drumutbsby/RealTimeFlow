# -*- coding: utf-8 -*-
"""Katman B — bilimsel finansal skorlama modelleri (PRD §13).

Finansal tablo girdisiyle akademik iflas/sağlamlık skorları hesaplar. Bu modül
YALNIZCA formülleri içerir; finansal tablo ÇEKİMİ ayrı bir connector işidir.

Bu turda uygulananlar (formülleri araştırma ajanıyla doğrulanacak):
  • Altman Z'' (imalat-dışı / gelişen piyasa) + EMS rating-eşdeğeri
  • Altman Z'  (halka kapalı imalat, defter değerli)
  • Piotroski F-Score (0-9 finansal sağlamlık)

Ertelenenler (kendi doğrulama turlarında): Ohlson O (9 katsayı + makro deflatör),
Beneish M (manipülasyon, iflas değil), Merton DD (piyasa verisi gerektirir).

⚠️ Tüm katsayılar ABD verisiyle kalibre; BIST için gelişen-piyasa varyantı
tercih edilir. Yüksek enflasyon muhasebesi (TMS 29) skorları bozabilir.
"""
from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass
class FinansalVeri:
    """Tek döneme ait finansal tablo girdileri (tümü aynı para birimi)."""
    toplam_aktif: float
    donen_varlik: float                 # current assets (CA)
    kisa_vadeli_borc: float             # current liabilities (CL)
    toplam_borc: float                  # total liabilities (TL)
    gecmis_yil_karlari: float           # retained earnings (RE)
    faiz_vergi_oncesi_kar: float        # EBIT
    satislar: float                     # net sales
    net_kar: float                      # net income (NI)
    # Piotroski / Ohlson için ek alanlar (opsiyonel)
    faaliyet_nakit_akisi: float | None = None   # CFO
    brut_kar: float | None = None               # gross profit
    uzun_vadeli_borc: float | None = None        # long-term debt
    hisse_adedi: float | None = None             # shares outstanding
    ffo: float | None = None                     # funds from operations (Ohlson)

    @property
    def ozkaynak_defter(self) -> float:
        """Defter değerli özkaynak = toplam aktif − toplam borç."""
        return self.toplam_aktif - self.toplam_borc

    @property
    def isletme_sermayesi(self) -> float:
        """Working capital = dönen varlık − kısa vadeli borç."""
        return self.donen_varlik - self.kisa_vadeli_borc


@dataclass
class ModelSonucu:
    model: str
    skor: float
    bolge: str                          # "güvenli" | "gri" | "sıkıntı" | "-"
    ayrinti: dict


def _bolge(skor: float, guvenli_esik: float, sikinti_esik: float) -> str:
    if skor > guvenli_esik:
        return "güvenli"
    if skor < sikinti_esik:
        return "sıkıntı"
    return "gri"


def altman_z2(fv: FinansalVeri) -> ModelSonucu | None:
    """Altman Z''-Score (imalat-dışı / gelişen piyasa).

    Z'' = 6.56·X1 + 3.26·X2 + 6.72·X3 + 1.05·X4
      X1 = işletme sermayesi / toplam aktif
      X2 = geçmiş yıl kârları / toplam aktif
      X3 = FVÖK / toplam aktif
      X4 = defter özkaynak / toplam borç
    Bölge (temel Z'' skoru): >2.6 güvenli, 1.1–2.6 gri, <1.1 sıkıntı.
    EMS rating-eşdeğeri = Z'' + 3.25 (gelişen piyasa; skor 0 ≈ temerrüt notu).
    """
    if fv.toplam_aktif <= 0 or fv.toplam_borc <= 0:
        return None
    x1 = fv.isletme_sermayesi / fv.toplam_aktif
    x2 = fv.gecmis_yil_karlari / fv.toplam_aktif
    x3 = fv.faiz_vergi_oncesi_kar / fv.toplam_aktif
    x4 = fv.ozkaynak_defter / fv.toplam_borc
    z2 = 6.56 * x1 + 3.26 * x2 + 6.72 * x3 + 1.05 * x4
    return ModelSonucu(
        "altman_z2", round(z2, 3), _bolge(z2, 2.6, 1.1),
        {"X1": round(x1, 4), "X2": round(x2, 4), "X3": round(x3, 4),
         "X4": round(x4, 4), "ems_rating_esdegeri": round(z2 + 3.25, 3)})


def altman_z_ozel(fv: FinansalVeri) -> ModelSonucu | None:
    """Altman Z'-Score (halka kapalı imalat; defter değerli X4).

    Z' = 0.717·X1 + 0.847·X2 + 3.107·X3 + 0.420·X4 + 0.998·X5
      X5 = satışlar / toplam aktif
    Bölge: >2.9 güvenli, 1.23–2.9 gri, <1.23 sıkıntı.
    """
    if fv.toplam_aktif <= 0 or fv.toplam_borc <= 0:
        return None
    x1 = fv.isletme_sermayesi / fv.toplam_aktif
    x2 = fv.gecmis_yil_karlari / fv.toplam_aktif
    x3 = fv.faiz_vergi_oncesi_kar / fv.toplam_aktif
    x4 = fv.ozkaynak_defter / fv.toplam_borc
    x5 = fv.satislar / fv.toplam_aktif
    z = 0.717 * x1 + 0.847 * x2 + 3.107 * x3 + 0.420 * x4 + 0.998 * x5
    return ModelSonucu(
        "altman_z_ozel", round(z, 3), _bolge(z, 2.9, 1.23),
        {"X1": round(x1, 4), "X2": round(x2, 4), "X3": round(x3, 4),
         "X4": round(x4, 4), "X5": round(x5, 4)})


def piotroski_f(cari: FinansalVeri,
                onceki: FinansalVeri) -> ModelSonucu | None:
    """Piotroski F-Score (0-9): finansal sağlamlık/kalite (iflas olasılığı DEĞİL).

    9 ikili kriter: kârlılık (4), kaldıraç/likidite (3), verimlilik (2).
    İki dönemlik veri gerektirir. Eksik alan varsa None.
    """
    for fv in (cari, onceki):
        if (fv.toplam_aktif <= 0 or fv.faaliyet_nakit_akisi is None
                or fv.brut_kar is None or fv.uzun_vadeli_borc is None
                or fv.hisse_adedi is None or fv.kisa_vadeli_borc <= 0
                or fv.satislar <= 0):
            return None
    roa_c = cari.net_kar / cari.toplam_aktif
    roa_o = onceki.net_kar / onceki.toplam_aktif
    puan = 0
    kriterler = {}
    # Kârlılık
    kriterler["roa_pozitif"] = roa_c > 0
    kriterler["cfo_pozitif"] = cari.faaliyet_nakit_akisi > 0
    kriterler["roa_artis"] = roa_c > roa_o
    kriterler["tahakkuk"] = (cari.faaliyet_nakit_akisi / cari.toplam_aktif) > roa_c
    # Kaldıraç / likidite / kaynak
    kriterler["kaldirac_azalis"] = (
        (cari.uzun_vadeli_borc / cari.toplam_aktif)
        < (onceki.uzun_vadeli_borc / onceki.toplam_aktif))
    kriterler["cari_oran_artis"] = (
        (cari.donen_varlik / cari.kisa_vadeli_borc)
        > (onceki.donen_varlik / onceki.kisa_vadeli_borc))
    kriterler["yeni_hisse_yok"] = cari.hisse_adedi <= onceki.hisse_adedi
    # Verimlilik
    kriterler["brut_marj_artis"] = (
        (cari.brut_kar / cari.satislar) > (onceki.brut_kar / onceki.satislar))
    kriterler["aktif_devir_artis"] = (
        (cari.satislar / cari.toplam_aktif)
        > (onceki.satislar / onceki.toplam_aktif))
    puan = sum(1 for v in kriterler.values() if v)
    bolge = "güvenli" if puan >= 7 else ("sıkıntı" if puan <= 2 else "gri")
    return ModelSonucu("piotroski_f", float(puan), bolge, kriterler)


def ohlson_o(cari: FinansalVeri, onceki: FinansalVeri,
             gsyh_deflator: float) -> ModelSonucu | None:
    """Ohlson O-Score (1980) — lojistik iflas olasılığı.

    O = -1.32 - 0.407·SIZE + 6.03·TLTA - 1.43·WCTA + 0.0757·CLCA
        - 1.72·OENEG - 2.37·NITA - 1.83·FUTL + 0.285·INTWO - 0.521·CHIN
      SIZE  = ln(toplam aktif / GSYH fiyat düzeyi endeksi)
      TLTA  = toplam borç / toplam aktif
      WCTA  = işletme sermayesi / toplam aktif
      CLCA  = kısa vadeli borç / dönen varlık
      OENEG = 1 eğer toplam borç > toplam aktif (özkaynak negatif) else 0
      NITA  = net kâr / toplam aktif
      FUTL  = FFO / toplam borç  (FFO yoksa CFO kullanılır)
      INTWO = 1 eğer son iki yıl net zarar else 0
      CHIN  = (NIt − NIt-1) / (|NIt| + |NIt-1|)
    Olasılık = 1 / (1 + e^(−O)). Bu katsayı seti Ohlson Model 1'dir (1 yıllık
    ufuk). Sınıflandırma: Ohlson'ın ampirik optimal kesimi ~0.038 (erken uyarı),
    0.5 ise naif/güçlü eşik. Bölge: >0.5 sıkıntı, >0.038 gri, altı güvenli.

    ⚠️ SIZE makro girdi ister: gsyh_deflator, toplam aktifin para-yıl birimiyle
    tutarlı fiyat düzeyi endeksi olmalı (Türkiye için TÜİK GSYH deflatörü);
    ABD dolar ölçeği doğrudan kullanılmaz.
    """
    ta = cari.toplam_aktif
    ffo = cari.ffo if cari.ffo is not None else cari.faaliyet_nakit_akisi
    if (ta <= 0 or cari.donen_varlik <= 0 or cari.toplam_borc <= 0
            or gsyh_deflator <= 0 or ffo is None):
        return None
    size = math.log(ta / gsyh_deflator)
    tlta = cari.toplam_borc / ta
    wcta = cari.isletme_sermayesi / ta
    clca = cari.kisa_vadeli_borc / cari.donen_varlik
    oeneg = 1.0 if cari.toplam_borc > ta else 0.0
    nita = cari.net_kar / ta
    futl = ffo / cari.toplam_borc
    intwo = 1.0 if (cari.net_kar < 0 and onceki.net_kar < 0) else 0.0
    nit, nip = cari.net_kar, onceki.net_kar
    payda = abs(nit) + abs(nip)
    chin = (nit - nip) / payda if payda > 0 else 0.0
    o = (-1.32 - 0.407 * size + 6.03 * tlta - 1.43 * wcta + 0.0757 * clca
         - 1.72 * oeneg - 2.37 * nita - 1.83 * futl + 0.285 * intwo
         - 0.521 * chin)
    olasilik = 1.0 / (1.0 + math.exp(-o))
    # Ohlson'ın ampirik optimal kesimi ~0.038 (erken uyarı); 0.5 naif/güçlü
    # eşiktir. İki kademe: >0.5 sıkıntı, >0.038 gri (erken uyarı), altı güvenli.
    if olasilik > 0.5:
        bolge = "sıkıntı"
    elif olasilik > 0.038:
        bolge = "gri"
    else:
        bolge = "güvenli"
    return ModelSonucu(
        "ohlson_o", round(o, 3), bolge,
        {"olasilik": round(olasilik, 4), "SIZE": round(size, 4),
         "TLTA": round(tlta, 4), "WCTA": round(wcta, 4),
         "CLCA": round(clca, 4), "NITA": round(nita, 4),
         "FUTL": round(futl, 4), "OENEG": oeneg, "INTWO": intwo,
         "CHIN": round(chin, 4)})
