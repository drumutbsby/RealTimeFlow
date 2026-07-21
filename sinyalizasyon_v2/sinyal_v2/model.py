# -*- coding: utf-8 -*-
"""Kanonik veri modeli — V2'nin çekirdek varlıkları.

PRD §11 ile uyumlu. İlke: ham kaynak verisi asla üzerine yazılmaz; türetilmiş
her değer (Sinyal, Skor) bir KaynakKaydi'na bağlanır → kanıt zinciri.

Faz 0'da hafif `dataclass`'lar kullanılır; kalıcılık (SQLite) ileriki fazda bu
modelin üzerine eklenir. Depolama teknolojisi buraya sızmaz.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import IntEnum


class Siddet(IntEnum):
    """Sinyal şiddeti. Sıralama V1 SEVERITY_ORDER ile uyumludur (0 = en ağır)."""
    KRITIK = 0
    YUKSEK = 1
    ORTA = 2
    DUSUK = 3

    @property
    def etiket(self) -> str:
        return {0: "KRİTİK", 1: "YÜKSEK", 2: "ORTA", 3: "DÜŞÜK"}[self.value]

    @classmethod
    def agirliktan(cls, agirlik: int) -> "Siddet":
        """V1'in ağırlık→şiddet eşlemesi: 9-10 KRİTİK, 7-8 YÜKSEK, 5-6 ORTA."""
        if agirlik >= 9:
            return cls.KRITIK
        if agirlik >= 7:
            return cls.YUKSEK
        if agirlik >= 5:
            return cls.ORTA
        return cls.DUSUK


class KaynakTipi(IntEnum):
    """Bir kaydın hangi kaynaktan geldiği. Kaynak güvenilirlik ağırlığı (PRD
    §10.5) bu tipe göre atanır: resmî kurum > derecelendirme > basın."""
    KAP = 1
    RESMI_GAZETE = 2
    ILAN_GOV = 3            # Basın İlan Kurumu (iflas/konkordato/icra/ihale)
    TICARET_SICIL = 4
    EKAP_YASAKLI = 5
    DERECELENDIRME = 6      # JCR Avrasya vb.
    SPK = 7
    HABER = 99             # Google News — skora KATILMAZ, yalnızca bilgi


# Kaynak güvenilirlik ağırlığı (0-1). Resmî kurum > derecelendirme > basın.
KAYNAK_GUVENILIRLIK: dict[KaynakTipi, float] = {
    KaynakTipi.KAP: 1.0,
    KaynakTipi.RESMI_GAZETE: 1.0,
    KaynakTipi.ILAN_GOV: 1.0,
    KaynakTipi.TICARET_SICIL: 1.0,
    KaynakTipi.EKAP_YASAKLI: 1.0,
    KaynakTipi.SPK: 1.0,
    KaynakTipi.DERECELENDIRME: 0.9,
    KaynakTipi.HABER: 0.0,   # skora girmez
}


@dataclass
class Firma:
    """Kanonik firma kaydı. Farklı kaynaklardaki varyantlar buraya bağlanır."""
    canonical_id: str
    unvan: str
    vkn: str | None = None
    mersis: str | None = None
    ticaret_sicil_no: str | None = None
    kap_oid: str | None = None            # halka açıklar (V1 uyumu)
    unvan_varyantlari: list[str] = field(default_factory=list)
    il: str | None = None
    sektor_nace: str | None = None
    halka_acik: bool = False


@dataclass
class KaynakKaydi:
    """Bir kaynaktan çekilmiş ham/normalize kayıt — kanıt zincirinin kökü."""
    id: str
    firma_id: str
    kaynak_tipi: KaynakTipi
    orijinal_kimlik: str                  # kaynaktaki id (ör. KAP disclosureIndex)
    cekim_zamani: datetime
    kaynak_url: str
    ham_veri: dict = field(default_factory=dict)


@dataclass
class Sinyal:
    """Sınıflandırılmış bir risk sinyali. Her zaman bir KaynakKaydi'na bağlıdır."""
    firma_id: str
    kategori_id: str
    kategori: str
    siddet: Siddet
    agirlik: int
    tarih: datetime
    kaynak_kaydi_id: str
    kaynak_tipi: KaynakTipi
    gerekce: str                          # neden bu sinyal (alıntı/kalıp)
    alinti: str = ""                      # kaynak metinden ilgili kesit
    kaynak_url: str = ""
    iyilesme: bool = False                # bozulma değil, olumlu gelişme mi?
    guncellik: float = 1.0               # güncellik çarpanı (V1 mantığı)


@dataclass
class SkorAnlik:
    """Bir firmanın belirli bir andaki skoru + açıklaması (açıklanabilirlik)."""
    firma_id: str
    tarih: datetime
    skor: float                           # 0-100
    notu: str                             # A-E
    model_surumu: str
    katman_a: float = 0.0                # olay/sinyal skoru
    katman_b: float | None = None        # finansal model skoru (varsa)
    guven: float = 1.0                   # veri yeterliliği (0-1)
    aciklama: list[str] = field(default_factory=list)  # katkı dökümü
