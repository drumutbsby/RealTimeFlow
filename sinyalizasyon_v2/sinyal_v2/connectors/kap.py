# -*- coding: utf-8 -*-
"""KAP connector — V2'nin ilk kaynağı (V1 KAP katmanının yeniden paketlenmişi).

Faz 0 kapsamı: V1'in kanıtlanmış **flight-payload ayrıştırıcısı** saf (ağdan
bağımsız, dolayısıyla test edilebilir) bir fonksiyon olarak taşınır ve KAP
bildirim sözlüğünü kanonik `KaynakKaydi`'na çeviren `ayristir` yazılır.

⚠️ MEKANİZMA DOĞRULAMASI (PRD §10.1 notu): Güncel KAP, veriyi gömülü flight
payload yerine **JSON REST endpoint** (`POST /tr/api/disclosure/members/
byCriteria`) ile sunuyor olabilir. `cek()` canlı bağlantı bu doğrulama
yapıldıktan sonra bağlanacaktır; şu an ağ çekimi dışarıdan enjekte edilen bir
`http_get` ile yapılır (bağımlılık tersine çevirme → test edilebilirlik) ve
bağlı değilse **sessizce başarı taklidi yapmaz**, açık bir başarısız sağlık
döner.
"""
from __future__ import annotations

import json
import re
from datetime import datetime
from typing import Callable

from ..model import KaynakKaydi, KaynakTipi
from ..normalize import norm
from .base import CekimSonucu, Connector, SaglikDurumu

BASE = "https://www.kap.org.tr"


def uye_rehberi_ayristir(page: str) -> list[dict]:
    """KAP üye rehberi sayfasına gömülü ihraççı listesini çıkar (V1 mantığı).

    → [{hisse, kodlar, unvan, oid, islem}]. Hisse kodu olmayan ihraççılar da
    dahildir (temerrüt takibi için kritik kesim). Canlı jcrer değil, KAP
    bildirim-sorgu sayfasıdır; yapı değişirse boş liste döner.
    """
    txt = page.replace('\\"', '"')
    satirlar, gorulen_oid, gorulen_etiket = [], set(), set()
    for chunk in txt.split('{"kapMemberOid"')[1:]:
        chunk = chunk[:2500]
        oid = re.search(r'"mkkMemberOid":"([0-9a-fA-F]+)"', chunk)
        ttl = re.search(r'"kapMemberTitle":"(.*?)"', chunk)
        if not (oid and ttl) or oid.group(1) in gorulen_oid:
            continue
        gorulen_oid.add(oid.group(1))
        title = ttl.group(1)
        try:
            title = json.loads('"' + title.replace('"', '\\"') + '"')
        except json.JSONDecodeError:
            pass
        stk = re.search(r'"stockCode":"(.*?)"', chunk)
        pis = re.search(r'"payIslemDurumu":"(.*?)"', chunk)
        kodlar = [c.strip().upper() for c in
                  (stk.group(1) if stk else "").replace(";", ",").split(",")
                  if c.strip() and c.strip() != "-"]
        if kodlar:
            kod = max(kodlar, key=len)            # birincil kod: en uzunu
            kodlar_str = ",".join(kodlar)
        else:
            kod = "*" + norm(title).split()[0].upper()[:9]  # kodsuz ihraççı
            kodlar_str = kod
        etiket, n = kod, 2
        while etiket in gorulen_etiket:
            etiket = f"{kod}{n}"
            n += 1
        gorulen_etiket.add(etiket)
        satirlar.append({"hisse": etiket, "kodlar": kodlar_str, "unvan": title,
                         "oid": oid.group(1),
                         "islem": pis.group(1) if pis else ""})
    return satirlar


def flight_dizisi_cikar(page: str, anchor: str = '\\"data\\":['):
    """Next.js SSR sayfasına gömülü (escape'li) JSON dizisini çıkar.

    V1 `extract_flight_array` ile aynı davranış:
      None → sayfada veri bloğu yok (bozuk/kısıtlı yanıt),
      []   → veri bloğu var ama boş (bildirimi yok).
    """
    start = page.find(anchor)
    if start < 0:
        return None
    region = page[start:start + 3_000_000]
    txt = (region.replace('\\\\"', "@@Q@@")
                 .replace('\\"', '"')
                 .replace("@@Q@@", '\\"'))
    a = txt.find("[")
    if a < 0:
        return None
    depth, in_str, esc = 0, False, False
    for i, ch in enumerate(txt[a:], a):
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
            continue
        if ch == '"':
            in_str = True
        elif ch == "[":
            depth += 1
        elif ch == "]":
            depth -= 1
            if depth == 0:
                try:
                    return json.loads(txt[a:i + 1])
                except json.JSONDecodeError:
                    return None          # ayrıştırılamayan blok "temiz" değil
    return None                          # dizi hiç kapanmadı: kesik yanıt


class KapConnector(Connector):
    kaynak_tipi = KaynakTipi.KAP

    def __init__(self, http_get: Callable[[str], str] | None = None):
        # http_get enjekte edilmezse cek() çalışmaz ama sessizce başarı taklidi
        # yapmaz — açık başarısız sağlık döner (sessiz veri kaybı yasak).
        self._http_get = http_get
        self._son_saglik = SaglikDurumu(kaynak_tipi=self.kaynak_tipi,
                                        basarili=True)

    def cek(self, sorgu: dict) -> CekimSonucu:
        oid = sorgu.get("oid")
        yil = sorgu.get("yil")
        if self._http_get is None:
            s = SaglikDurumu(
                kaynak_tipi=self.kaynak_tipi, basarili=False,
                hata="http_get enjekte edilmedi — canlı KAP mekanizması "
                     "(flight payload vs JSON REST) doğrulanıp bağlanmalı")
            self._son_saglik = s
            return CekimSonucu(saglik=s)
        url = (f"{BASE}/tr/bildirim-sorgu-sonuc?srcbar=Y&cmp=Y&cat=2"
               f"&m={oid}&t=X&slf=ALL")
        if yil:
            url += f"&yr={yil}"
        try:
            page = self._http_get(url)
            arr = flight_dizisi_cikar(page)
        except Exception as exc:                       # noqa: BLE001
            s = SaglikDurumu(kaynak_tipi=self.kaynak_tipi, basarili=False,
                             hata=str(exc))
            self._son_saglik = s
            return CekimSonucu(saglik=s)
        if arr is None:
            s = SaglikDurumu(kaynak_tipi=self.kaynak_tipi, basarili=False,
                             hata="veri bloğu bulunamadı (kısıtlama/bozuk yanıt)")
            self._son_saglik = s
            return CekimSonucu(saglik=s)
        kayitlar = [(it.get("disclosureBasic") or it) for it in arr]
        s = SaglikDurumu(kaynak_tipi=self.kaynak_tipi, basarili=True,
                         cekilen_kayit=len(kayitlar))
        self._son_saglik = s
        return CekimSonucu(saglik=s, ham_kayitlar=kayitlar)

    def ayristir(self, ham: dict, firma_id: str) -> KaynakKaydi:
        idx = ham.get("disclosureIndex")
        return KaynakKaydi(
            id=f"kap:{idx}",
            firma_id=firma_id,
            kaynak_tipi=self.kaynak_tipi,
            orijinal_kimlik=str(idx),
            cekim_zamani=datetime.now(),
            kaynak_url=f"{BASE}/tr/Bildirim/{idx}",
            ham_veri=ham,
        )

    def olay_tarihi(self, ham: dict) -> datetime:
        """KAP publishDate ('%d.%m.%Y %H:%M:%S') → datetime; çözülemezse min."""
        s = (ham.get("publishDate") or "").strip()
        try:
            return datetime.strptime(s, "%d.%m.%Y %H:%M:%S")
        except ValueError:
            try:
                return datetime.strptime(s[:10], "%d.%m.%Y")
            except ValueError:
                return datetime.min

    def saglik(self) -> SaglikDurumu:
        return self._son_saglik
