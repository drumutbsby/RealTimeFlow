# -*- coding: utf-8 -*-
"""JCR Eurasia (Avrasya) connector — kredi derecelendirme notları.

Kaynak: jcrer.com.tr — kamuya açık, girişsiz HTML tablo (araştırma ajanı 🟢).
Sayfa tek bir tablo taşır; her firma İKİ satırdır (uzun vade + kısa vade).
Uzun-vade satırı firma adı, uluslararası/yerel not, görünüm, rapor tarihi ve
sektörü içerir. Parser bu satırları çıkarır; not YÖNÜ (görünüm negatif vb.)
mevcut sinyal motoruyla sınıflandırılır.

⚠️ Site HTML yapısı değişebilir → parser izole ve testlidir; canlı çekim
başarısızlığı sessizce "temiz" sayılmaz (SaglikDurumu.basarili=False).
"""
from __future__ import annotations

import html as html_lib
import re
from datetime import datetime
from typing import Callable

from ..model import KaynakKaydi, KaynakTipi
from .base import CekimSonucu, Connector, SaglikDurumu

BASE = "https://www.jcrer.com.tr"
LISTE_URL = f"{BASE}/tr/derecelendirme/raporlar/kredi-derecelendirme"


def _hucreler(tr_html: str) -> list[str]:
    """Bir <tr> içindeki hücre metinlerini (etiketsiz, unescape) döndür."""
    ham = re.findall(r"<t[hd][^>]*>(.*?)</t[hd]>", tr_html, re.S | re.I)
    out = []
    for c in ham:
        c = re.sub(r"<[^>]+>", " ", c)          # iç etiketleri at
        c = html_lib.unescape(c)                 # &#214; → Ö, &#160; → \xa0
        c = c.replace("\xa0", " ")
        out.append(re.sub(r"\s+", " ", c).strip())
    return out


def derecelendirmeleri_ayristir(html: str) -> list[dict]:
    """JCR liste sayfasından firma-bazlı derecelendirme kayıtları çıkar.

    Her kayıt: unvan, uluslararası (YP/YL) not, görünüm, yerel not,
    yerel görünüm, rapor tarihi, sektör. Uzun-vade satırları esas alınır.
    """
    m = re.search(r"<table.*?</table>", html, re.S | re.I)
    if not m:
        return []
    satirlar = re.findall(r"<tr.*?</tr>", m.group(0), re.S | re.I)
    kayitlar = []
    for tr in satirlar:
        h = _hucreler(tr)
        # uzun-vade veri satırı: 2. hücre "UZUN VADE" ve 1. hücre firma adı
        if len(h) < 11 or h[1].upper() != "UZUN VADE" or not h[0]:
            continue
        kayitlar.append({
            "unvan": h[0],
            "uluslararasi_yp": h[2], "uluslararasi_yl": h[3],
            "uluslararasi_gorunum": h[4],
            "yerel_not": h[5], "yerel_gorunum": h[6],
            "tarih": h[9], "sektor": h[10],
        })
    return kayitlar


class JcrConnector(Connector):
    kaynak_tipi = KaynakTipi.DERECELENDIRME

    def __init__(self, http_get: Callable[[str], str] | None = None):
        self._http_get = http_get
        self._son_saglik = SaglikDurumu(kaynak_tipi=self.kaynak_tipi,
                                        basarili=True)

    def cek(self, sorgu: dict) -> CekimSonucu:
        if self._http_get is None:
            s = SaglikDurumu(kaynak_tipi=self.kaynak_tipi, basarili=False,
                             hata="http_get enjekte edilmedi")
            self._son_saglik = s
            return CekimSonucu(saglik=s)
        try:
            html = self._http_get(LISTE_URL)
            kayitlar = derecelendirmeleri_ayristir(html)
        except Exception as exc:                       # noqa: BLE001
            s = SaglikDurumu(kaynak_tipi=self.kaynak_tipi, basarili=False,
                             hata=str(exc))
            self._son_saglik = s
            return CekimSonucu(saglik=s)
        if not kayitlar:
            s = SaglikDurumu(kaynak_tipi=self.kaynak_tipi, basarili=False,
                             hata="tablo bulunamadı/boş (yapı değişmiş olabilir)")
            self._son_saglik = s
            return CekimSonucu(saglik=s)
        s = SaglikDurumu(kaynak_tipi=self.kaynak_tipi, basarili=True,
                         cekilen_kayit=len(kayitlar))
        self._son_saglik = s
        return CekimSonucu(saglik=s, ham_kayitlar=kayitlar)

    def ayristir(self, ham: dict, firma_id: str) -> KaynakKaydi:
        anahtar = re.sub(r"\W+", "-", ham.get("unvan", "")).strip("-").lower()[:40]
        return KaynakKaydi(
            id=f"jcr:{anahtar}:{ham.get('tarih', '')}",
            firma_id=firma_id, kaynak_tipi=self.kaynak_tipi,
            orijinal_kimlik=anahtar, cekim_zamani=datetime.now(),
            kaynak_url=LISTE_URL, ham_veri=ham)

    def yuzey_metin(self, ham: dict) -> str:
        # motor RATING mantığı: "derecelendirme"/"görünüm" tetikler,
        # "negatif" olumsuz yön verir; "durağan"/"pozitif" nötr/olumlu
        return (f"Kredi derecelendirme: {ham.get('unvan','')} — yerel not "
                f"{ham.get('yerel_not','')}, görünüm {ham.get('yerel_gorunum','')}"
                f", uluslararası {ham.get('uluslararasi_yp','')}/"
                f"{ham.get('uluslararasi_yl','')} görünüm "
                f"{ham.get('uluslararasi_gorunum','')}")

    def olay_tarihi(self, ham: dict) -> datetime:
        try:
            return datetime.strptime(ham.get("tarih", "")[:10], "%d.%m.%Y")
        except ValueError:
            return datetime.min

    def saglik(self) -> SaglikDurumu:
        return self._son_saglik
