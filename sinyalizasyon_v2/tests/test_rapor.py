# -*- coding: utf-8 -*-
"""rapor.py birim testleri — metin ve CSV render."""
from datetime import datetime

from sinyal_v2.model import Firma, KaynakTipi, Siddet, Sinyal
from sinyal_v2.rapor import firma_raporu_metin, sinyaller_csv
from sinyal_v2.skor import firma_skoru

SIMDI = datetime(2026, 6, 1)


def _sinyal(kategori_id, kategori, agirlik, iyilesme=False):
    return Sinyal(
        firma_id="c1", kategori_id=kategori_id, kategori=kategori,
        siddet=Siddet.agirliktan(agirlik), agirlik=agirlik,
        tarih=datetime(2026, 5, 15), kaynak_kaydi_id="kap:1",
        kaynak_tipi=KaynakTipi.KAP, gerekce=f"'{kategori_id}' ifadesi",
        kaynak_url="https://www.kap.org.tr/tr/Bildirim/1", iyilesme=iyilesme)


def test_metin_rapor_icerigi():
    firma = Firma(canonical_id="c1", unvan="Test Sanayi A.Ş.", vkn="8760047464")
    sinyaller = [_sinyal("iflas", "İflas / Tasfiye", 10),
                 _sinyal("regulator", "Regülatör Cezası", 7)]
    skor = firma_skoru(sinyaller, SIMDI)
    metin = firma_raporu_metin(firma, skor, sinyaller)
    assert "Test Sanayi A.Ş." in metin
    assert "8760047464" in metin
    assert "Not:" in metin and "Skor:" in metin
    assert "İflas / Tasfiye" in metin
    assert "yatırım tavsiyesi değildir".lower() in metin.lower()


def test_temiz_firma_raporu():
    firma = Firma(canonical_id="c1", unvan="Temiz A.Ş.")
    skor = firma_skoru([], SIMDI)
    metin = firma_raporu_metin(firma, skor, [])
    assert "Risk sinyali yok." in metin


def test_iyilesme_ayri_bolum():
    firma = Firma(canonical_id="c1", unvan="X A.Ş.")
    sinyaller = [_sinyal("yakin_izleme", "Yakın İzleme", 0, iyilesme=True)]
    skor = firma_skoru(sinyaller, SIMDI)
    metin = firma_raporu_metin(firma, skor, sinyaller)
    assert "İyileşme sinyalleri" in metin


def test_csv_baslik_ve_satirlar():
    sinyaller = [_sinyal("iflas", "İflas", 10),
                 _sinyal("icra", "İcra", 7)]
    csv_metin = sinyaller_csv(sinyaller)
    satirlar = csv_metin.strip().splitlines()
    assert satirlar[0].startswith("firma_id,tarih,siddet")
    assert len(satirlar) == 3          # başlık + 2 sinyal
    assert "KRİTİK" in csv_metin and "İflas" in csv_metin
