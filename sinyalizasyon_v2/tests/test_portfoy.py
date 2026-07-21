# -*- coding: utf-8 -*-
"""Portföy/izleme listesi tablo render testleri."""
from datetime import datetime

from sinyal_v2.model import KaynakTipi, Siddet, Sinyal
from sinyal_v2.rapor import portfoy_satiri, portfoy_tablosu
from sinyal_v2.skor import firma_skoru

SIMDI = datetime(2026, 6, 1)


def _sinyal(agirlik, kategori_id="iflas"):
    return Sinyal(
        firma_id="c1", kategori_id=kategori_id, kategori=kategori_id.upper(),
        siddet=Siddet.agirliktan(agirlik), agirlik=agirlik, tarih=SIMDI,
        kaynak_kaydi_id="k", kaynak_tipi=KaynakTipi.KAP, gerekce="")


def test_portfoy_satiri_siddet_sayimi():
    sinyaller = [_sinyal(10), _sinyal(7, "icra")]     # 1 kritik + 1 yüksek
    skor = firma_skoru(sinyaller, SIMDI)
    satir = portfoy_satiri("SASA", "SASA A.Ş.", skor, sinyaller)
    assert satir["kritik"] == 1 and satir["yuksek"] == 1
    assert satir["toplam"] == 2 and satir["hisse"] == "SASA"


def test_portfoy_tablosu_skora_gore_siralar():
    r_yuksek = {"hisse": "AAA", "unvan": "Yüksek Risk A.Ş.", "skor": 60.0,
                "notu": "D", "kritik": 1, "yuksek": 1, "orta": 0, "dusuk": 0,
                "toplam": 2}
    r_dusuk = {"hisse": "BBB", "unvan": "Düşük Risk A.Ş.", "skor": 5.0,
               "notu": "B", "kritik": 0, "yuksek": 0, "orta": 0, "dusuk": 1,
               "toplam": 1}
    tablo = portfoy_tablosu([r_dusuk, r_yuksek])   # sırasız ver
    satirlar = tablo.splitlines()
    # başlık + çizgiler var, yüksek riskli firma düşükten ÖNCE
    assert "RİSK SIRALAMASI" in tablo
    aaa = next(i for i, s in enumerate(satirlar) if s.startswith("AAA"))
    bbb = next(i for i, s in enumerate(satirlar) if s.startswith("BBB"))
    assert aaa < bbb


def test_portfoy_tablosu_iyilesme_sayilmaz():
    iyi = Sinyal(firma_id="c1", kategori_id="dava", kategori="Dava",
                 siddet=Siddet.DUSUK, agirlik=0, tarih=SIMDI,
                 kaynak_kaydi_id="k", kaynak_tipi=KaynakTipi.KAP, gerekce="",
                 iyilesme=True)
    skor = firma_skoru([iyi], SIMDI)
    satir = portfoy_satiri("X", "X A.Ş.", skor, [iyi])
    assert satir["toplam"] == 0                # iyileşme risk sayılmaz
