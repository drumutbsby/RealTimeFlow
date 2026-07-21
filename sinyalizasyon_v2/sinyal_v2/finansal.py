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


def tum_modeller(fv: "FinansalVeri | None" = None,
                 onceki: "FinansalVeri | None" = None,
                 gsyh_deflator: float | None = None,
                 beneish: "BeneishGirdi | None" = None,
                 beneish_onceki: "BeneishGirdi | None" = None,
                 merton_ozkaynak: float | None = None,
                 merton_vol: float | None = None,
                 merton_borc: float | None = None) -> list[ModelSonucu]:
    """Verili girdilere göre uygulanabilir TÜM Katman B modellerini çalıştır.

    "Firmaları bilimsel değerlendirmeye tabi tutan yapı" cephesi: eksik girdi olan
    modeller sessizce atlanır (None), varsa hepsi bir liste olarak döner.
    """
    sonuclar: list[ModelSonucu] = []
    if fv is not None:
        for f in (altman_z2, altman_z_ozel):
            r = f(fv)
            if r:
                sonuclar.append(r)
        if onceki is not None:
            p = piotroski_f(fv, onceki)
            if p:
                sonuclar.append(p)
            if gsyh_deflator:
                o = ohlson_o(fv, onceki, gsyh_deflator)
                if o:
                    sonuclar.append(o)
    if beneish is not None and beneish_onceki is not None:
        b = beneish_m(beneish, beneish_onceki)
        if b:
            sonuclar.append(b)
    if merton_ozkaynak and merton_vol and merton_borc:
        m = merton_dd(merton_ozkaynak, merton_vol, merton_borc)
        if m:
            sonuclar.append(m)
    return sonuclar


def _normal_cdf(x: float) -> float:
    """Standart normal birikimli dağılım N(x) — math.erf ile (bağımlılıksız)."""
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def merton_dd(piyasa_ozkaynak: float, ozkaynak_volatilite: float, borc: float,
              risksiz_faiz: float = 0.10, vade_yil: float = 1.0
              ) -> ModelSonucu | None:
    """Naive Merton Distance-to-Default (Bharath & Shumway, 2008).

    Piyasa verisi (piyasa özkaynak değeri + özkaynak volatilitesi) gerektirir →
    YALNIZCA halka açık firmalara uygulanır. İki-denklemli sistem yerine naive
    yaklaşım kullanılır (V=E+D, σV ağırlıklı ortalama); erken uyarı için tam
    çözüme yakın ayırıcılık verir.

    DD = [ln(V/D) + (r − ½σV²)·T] / (σV·√T);  temerrüt olasılığı = N(−DD).
    """
    e, se, d = piyasa_ozkaynak, ozkaynak_volatilite, borc
    if e <= 0 or se <= 0 or d <= 0 or vade_yil <= 0:
        return None
    v = e + d
    sd = 0.05 + 0.25 * se                    # naive borç volatilitesi
    sv = (e / v) * se + (d / v) * sd         # naive varlık volatilitesi
    dd = ((math.log(v / d) + (risksiz_faiz - 0.5 * sv * sv) * vade_yil)
          / (sv * math.sqrt(vade_yil)))
    pd = _normal_cdf(-dd)
    bolge = ("sıkıntı" if pd > 0.10 else ("gri" if pd > 0.01 else "güvenli"))
    return ModelSonucu(
        "merton_dd_naive", round(dd, 3), bolge,
        {"temerrut_olasiligi": round(pd, 5), "sigma_V": round(sv, 4),
         "V": round(v, 2), "yorum": "yalnızca halka açık (piyasa verili) firma"})


@dataclass
class BeneishGirdi:
    """Beneish M-Score için tek döneme ait kalemler (iki dönem gerekir)."""
    satislar: float                     # net satışlar
    satis_maliyeti: float               # SMM (COGS)
    ticari_alacaklar: float             # net ticari alacaklar
    donen_varlik: float                 # dönen varlık
    maddi_duran_varlik: float           # net maddi duran varlık (PP&E)
    toplam_aktif: float
    amortisman: float                   # dönem amortismanı
    faaliyet_giderleri: float           # pazarlama+genel yönetim (SG&A)
    toplam_borc: float
    net_kar: float                      # sürdürülen faaliyet kârı
    faaliyet_nakit_akisi: float         # CFO


def beneish_m(cari: BeneishGirdi, onceki: BeneishGirdi) -> ModelSonucu | None:
    """Beneish M-Score — kazanç/tablo MANİPÜLASYONU kırmızı-bayrağı (iflas DEĞİL).

    M = -4.84 + 0.920·DSRI + 0.528·GMI + 0.404·AQI + 0.892·SGI + 0.115·DEPI
        - 0.172·SGAI + 4.679·TATA - 0.327·LVGI
    Eşik: M > -1.78 → manipülasyon olasılığı YÜKSEK ("şüpheli").

    ⚠️ Bu skor iflas/temerrüt tahmini DEĞİLDİR; ayrı bir kazanç-kalitesi
    sinyalidir ve iflas skoruna doğrudan ağırlık olarak eklenmez.
    """
    def guvenli_bol(a, b):
        return a / b if b else None
    gm_t = guvenli_bol(cari.satislar - cari.satis_maliyeti, cari.satislar)
    gm_o = guvenli_bol(onceki.satislar - onceki.satis_maliyeti, onceki.satislar)
    aqi_pay = 1 - guvenli_bol(cari.donen_varlik + cari.maddi_duran_varlik,
                              cari.toplam_aktif) if cari.toplam_aktif else None
    aqi_payda = (1 - guvenli_bol(onceki.donen_varlik + onceki.maddi_duran_varlik,
                                 onceki.toplam_aktif)
                 if onceki.toplam_aktif else None)
    dep_t = guvenli_bol(cari.amortisman,
                        cari.amortisman + cari.maddi_duran_varlik)
    dep_o = guvenli_bol(onceki.amortisman,
                        onceki.amortisman + onceki.maddi_duran_varlik)
    try:
        dsri = ((cari.ticari_alacaklar / cari.satislar) /
                (onceki.ticari_alacaklar / onceki.satislar))
        gmi = gm_o / gm_t
        aqi = aqi_pay / aqi_payda
        sgi = cari.satislar / onceki.satislar
        depi = dep_o / dep_t
        sgai = ((cari.faaliyet_giderleri / cari.satislar) /
                (onceki.faaliyet_giderleri / onceki.satislar))
        lvgi = ((cari.toplam_borc / cari.toplam_aktif) /
                (onceki.toplam_borc / onceki.toplam_aktif))
        tata = (cari.net_kar - cari.faaliyet_nakit_akisi) / cari.toplam_aktif
    except (TypeError, ZeroDivisionError):
        return None
    m = (-4.84 + 0.920 * dsri + 0.528 * gmi + 0.404 * aqi + 0.892 * sgi
         + 0.115 * depi - 0.172 * sgai + 4.679 * tata - 0.327 * lvgi)
    bolge = "şüpheli" if m > -1.78 else "temiz"
    return ModelSonucu(
        "beneish_m", round(m, 3), bolge,
        {"DSRI": round(dsri, 3), "GMI": round(gmi, 3), "AQI": round(aqi, 3),
         "SGI": round(sgi, 3), "DEPI": round(depi, 3), "SGAI": round(sgai, 3),
         "TATA": round(tata, 3), "LVGI": round(lvgi, 3),
         "yorum": "manipülasyon kırmızı-bayrağı (iflas değil)"})


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
