# -*- coding: utf-8 -*-
"""Basit, kaynağa saygılı HTTP çekim yardımcısı.

V1'in KAP dostu davranışının hafif genelleştirmesi: keep-alive oturum, kimlik
başlığı, küresel asgari istek aralığı (hız sınırlama). Connector'lara `http_get`
olarak enjekte edilir; böylece connector'lar test edilebilir kalır (ağ dışarıdan
gelir) ve tüm kaynaklar aynı nazik davranışı paylaşır.
"""
from __future__ import annotations

import json
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


def _hiz_sinirla() -> None:
    with _kilit:
        bekle = MIN_ARALIK - (time.time() - _son[0])
        if bekle > 0:
            time.sleep(bekle)
        _son[0] = time.time()


def get(url: str, timeout: int = TIMEOUT) -> str:
    """URL'yi hız sınırlamalı olarak çek → metin. Hata → istisna (connector
    bunu SaglikDurumu.basarili=False'a çevirir; sessiz kayıp yok)."""
    _hiz_sinirla()
    resp = _session.get(url, timeout=timeout)
    resp.raise_for_status()
    resp.encoding = "utf-8"
    return resp.text


def post_json(url: str, govde: dict, timeout: int = TIMEOUT) -> str:
    """URL'ye JSON gövde POST et → yanıt metni (hız sınırlamalı)."""
    _hiz_sinirla()
    resp = _session.post(url, data=json.dumps(govde), timeout=timeout,
                         headers={"Content-Type": "application/json",
                                  "Accept": "application/json"})
    resp.raise_for_status()
    resp.encoding = "utf-8"
    return resp.text
