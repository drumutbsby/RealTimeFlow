# -*- coding: utf-8 -*-
"""Basit, kaynağa saygılı HTTP çekim yardımcısı.

V1'in KAP dostu davranışının hafif genelleştirmesi: keep-alive oturum, kimlik
başlığı, küresel asgari istek aralığı (hız sınırlama). Connector'lara `http_get`
olarak enjekte edilir; böylece connector'lar test edilebilir kalır (ağ dışarıdan
gelir) ve tüm kaynaklar aynı nazik davranışı paylaşır.
"""
from __future__ import annotations

import threading
import time

import requests

MIN_ARALIK = 0.5          # istekler arası küresel asgari aralık (sn)
TIMEOUT = 40

_session = requests.Session()
_session.headers.update({
    "User-Agent": ("Mozilla/5.0 (compatible; SinyalizasyonV2/0.1; "
                   "+risk-arastirma)"),
    "Accept": "text/html,*/*", "Accept-Language": "tr",
})
_kilit = threading.Lock()
_son = [0.0]


def get(url: str, timeout: int = TIMEOUT) -> str:
    """URL'yi hız sınırlamalı olarak çek → metin. Hata → istisna (connector
    bunu SaglikDurumu.basarili=False'a çevirir; sessiz kayıp yok)."""
    with _kilit:
        bekle = MIN_ARALIK - (time.time() - _son[0])
        if bekle > 0:
            time.sleep(bekle)
        _son[0] = time.time()
    resp = _session.get(url, timeout=timeout)
    resp.raise_for_status()
    resp.encoding = "utf-8"
    return resp.text
