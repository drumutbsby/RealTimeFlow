# -*- coding: utf-8 -*-
"""Connector sözleşmesi — tüm kaynakların uyduğu ortak arayüz.

Tasarım (PRD §14.2): her kaynak `cek → ayristir → saglik` üçlüsünü uygular.
Çekirdek, connector'ları bu soyut arayüz üzerinden çağırır; bir kaynağın
site/HTML yapısı değişse bile yalnızca ilgili connector değişir.

Ortak dayanıklılık ilkeleri (V1'den genelleştirilir, PRD §14.2):
  • kaynak dostu hız sınırlama + devre kesici + üstel geri çekilme
  • başarısızlık ASLA sessiz "temiz firma" sayılmaz → `SaglikDurumu` ile
    açıkça işaretlenir (sessiz veri kaybı yasak).
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime

from ..model import KaynakKaydi, KaynakTipi


@dataclass
class SaglikDurumu:
    """Bir çekim denemesinin sonucu. `basarili=False` → veri eksik, gizleme."""
    kaynak_tipi: KaynakTipi
    basarili: bool
    cekilen_kayit: int = 0
    hata: str | None = None
    son_deneme: datetime | None = None
    kismi_veri: bool = False              # bir kısmı geldi (ör. bazı yıllar)


@dataclass
class CekimSonucu:
    """cek() çıktısı: ham kayıtlar + sağlık. Sağlık her zaman döner."""
    saglik: SaglikDurumu
    ham_kayitlar: list[dict] = field(default_factory=list)


class Connector(ABC):
    """Tek bir kaynağı çeken/ayrıştıran izole modül."""

    #: Bu connector'ın beslediği kaynak tipi (alt sınıf tanımlar)
    kaynak_tipi: KaynakTipi

    @abstractmethod
    def cek(self, sorgu: dict) -> CekimSonucu:
        """Kaynaktan ham kayıtları çek. `sorgu` kaynağa özgüdür (ör. firma
        oid'i, VKN, unvan, tarih aralığı). Ağ hatasında istisna FIRLATMAZ;
        `CekimSonucu.saglik.basarili=False` döner (sessiz kayıp yasak)."""
        raise NotImplementedError

    @abstractmethod
    def ayristir(self, ham: dict, firma_id: str) -> KaynakKaydi:
        """Tek bir ham kaydı kanonik `KaynakKaydi`'na çevir."""
        raise NotImplementedError

    def saglik(self) -> SaglikDurumu:
        """Son çekim sağlığı (izleme paneli için). Alt sınıf son durumu tutar."""
        return SaglikDurumu(kaynak_tipi=self.kaynak_tipi, basarili=True)
