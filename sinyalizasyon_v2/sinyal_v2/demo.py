# -*- coding: utf-8 -*-
"""Gösterim (demo) verisi — SENTETİK.

Canlı kaynak connector'ları bağlanana kadar boru hattını uçtan uca çalışır
göstermek için kullanılır. Gerçek firma/bildirim DEĞİLDİR; yalnızca örnek
KAP-benzeri kayıtlardır.
"""
from __future__ import annotations

from .model import Firma


def _kap(idx: int, title: str, summary: str, tarih: str) -> dict:
    return {"disclosureIndex": idx, "title": title, "summary": summary,
            "publishDate": tarih}


def demo_veri() -> list[tuple[Firma, list[dict]]]:
    """(Firma, ham KAP-benzeri kayıtlar) listesi döndür — gösterim amaçlı."""
    return [
        (Firma(canonical_id="c-batik", unvan="Örnek Batık Sanayi A.Ş."),
         [_kap(101, "Özel Durum Açıklaması", "Konkordato Başvurusu Hakkında",
               "10.06.2026 09:00:00"),
          _kap(102, "Özel Durum Açıklaması (Genel)",
               "Kredi Anapara Ödemesinin Vadesinde Ödenmemesi",
               "02.06.2026 10:00:00"),
          _kap(103, "Özel Durum Açıklaması", "İhtiyati Haciz Kararı Hakkında",
               "20.05.2026 14:00:00"),
          _kap(104, "Kar Payı Dağıtım İşlemleri",
               "2025 Yılı Kar Payı Dağıtımı", "01.04.2026 10:00:00")]),  # rutin
        (Firma(canonical_id="c-orta", unvan="Örnek Orta Ticaret A.Ş."),
         [_kap(201, "Özel Durum Açıklaması (Genel)",
               "SPK Tarafından İdari Para Cezası Uygulanması",
               "15.05.2026 11:00:00"),
          _kap(202, "Genel Kurul İşlemlerine İlişkin Bildirim",
               "2025 Olağan Genel Kurul Toplantısı Daveti",
               "01.05.2026 10:00:00")]),  # rutin
        (Firma(canonical_id="c-temiz", unvan="Örnek Temiz Holding A.Ş."),
         [_kap(301, "Sürdürülebilirlik Raporu", "2025 Sürdürülebilirlik Raporu",
               "01.05.2026 10:00:00"),  # gürültü
          _kap(302, "Pay Alım Satım Bildirimi", "Ortağın Pay Alımı",
               "10.05.2026 10:00:00")]),
    ]
