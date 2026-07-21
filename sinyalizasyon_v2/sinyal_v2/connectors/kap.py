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


BYCRITERIA_URL = f"{BASE}/tr/api/disclosure/members/byCriteria"


def bycriteria_govde(oid: str, bas_tarih: str, bit_tarih: str) -> dict:
    """KAP disclosure JSON REST endpoint istek gövdesi (tarih: YYYY-MM-DD)."""
    return {
        "fromDate": bas_tarih, "toDate": bit_tarih, "year": "", "prd": "",
        "term": "", "ruleType": "", "bdkReview": "", "disclosureClass": "",
        "index": "", "market": "", "isLate": "", "subjectList": [],
        "mkkMemberOidList": [oid], "inactiveMkkMemberOidList": [],
        "bdkMemberOidList": [], "mainSector": "", "sector": "", "subSector": "",
        "memberType": "IGS", "fromSrc": "", "srcCategory": "", "discIndex": [],
    }


class KapConnector(Connector):
    """KAP connector — disclosure'lar JSON REST (byCriteria) ile çekilir.

    (Eski gömülü 'flight payload' mekanizması KAP'ta kalktı; `flight_dizisi_cikar`
    geriye dönük/legacy olarak korunur.) Ağ dışarıdan `http_post` ile enjekte
    edilir → connector test edilebilir kalır.
    """
    kaynak_tipi = KaynakTipi.KAP

    def __init__(self, http_post: Callable[[str, dict], str] | None = None):
        self._http_post = http_post
        self._son_saglik = SaglikDurumu(kaynak_tipi=self.kaynak_tipi,
                                        basarili=True)

    @staticmethod
    def _yillik_pencereler(bas: str, bit: str) -> list[tuple[str, str]]:
        """[bas, bit] aralığını yıllık pencerelere böl (KAP çok-yıllık sorguda
        500 döner). Tarihler 'YYYY-MM-DD'."""
        try:
            b = datetime.strptime(bas, "%Y-%m-%d")
            e = datetime.strptime(bit, "%Y-%m-%d")
        except ValueError:
            return [(bas, bit)]                  # ayrıştırılamazsa tek pencere
        pencereler = []
        for yil in range(b.year, e.year + 1):
            p_bas = max(b, datetime(yil, 1, 1)).strftime("%Y-%m-%d")
            p_bit = min(e, datetime(yil, 12, 31)).strftime("%Y-%m-%d")
            pencereler.append((p_bas, p_bit))
        return pencereler

    def cek(self, sorgu: dict) -> CekimSonucu:
        """sorgu: {oid, bas_tarih 'YYYY-MM-DD', bit_tarih 'YYYY-MM-DD'}.

        Aralık yıllık pencerelere bölünüp birleştirilir; bir pencere hata verse
        de diğerleri kullanılır (kısmi veri açıkça işaretlenir — sessiz kayıp yok).
        """
        if self._http_post is None:
            s = SaglikDurumu(kaynak_tipi=self.kaynak_tipi, basarili=False,
                             hata="http_post enjekte edilmedi")
            self._son_saglik = s
            return CekimSonucu(saglik=s)
        oid = sorgu.get("oid", "")
        pencereler = self._yillik_pencereler(sorgu.get("bas_tarih", ""),
                                             sorgu.get("bit_tarih", ""))
        gorulen: dict = {}
        basari, hata = 0, 0
        son_hata = None
        for p_bas, p_bit in pencereler:
            try:
                arr = json.loads(self._http_post(
                    BYCRITERIA_URL, bycriteria_govde(oid, p_bas, p_bit)))
            except Exception as exc:                   # noqa: BLE001
                hata += 1
                son_hata = str(exc)
                continue
            if not isinstance(arr, list):
                hata += 1
                continue
            basari += 1
            for it in arr:
                idx = it.get("disclosureIndex")
                if idx is not None:
                    gorulen[idx] = it
        if basari == 0:
            s = SaglikDurumu(kaynak_tipi=self.kaynak_tipi, basarili=False,
                             hata=son_hata or "tüm pencereler başarısız")
            self._son_saglik = s
            return CekimSonucu(saglik=s)
        kayitlar = list(gorulen.values())
        s = SaglikDurumu(kaynak_tipi=self.kaynak_tipi, basarili=True,
                         cekilen_kayit=len(kayitlar), kismi_veri=hata > 0)
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
