# -*- coding: utf-8 -*-
"""model.py birim testleri."""
from datetime import datetime

from sinyal_v2.model import (KAYNAK_GUVENILIRLIK, Firma, KaynakKaydi,
                             KaynakTipi, Siddet, Sinyal)


def test_siddet_agirliktan_v1_uyumu():
    assert Siddet.agirliktan(10) is Siddet.KRITIK
    assert Siddet.agirliktan(9) is Siddet.KRITIK
    assert Siddet.agirliktan(8) is Siddet.YUKSEK
    assert Siddet.agirliktan(7) is Siddet.YUKSEK
    assert Siddet.agirliktan(6) is Siddet.ORTA
    assert Siddet.agirliktan(5) is Siddet.ORTA
    assert Siddet.agirliktan(4) is Siddet.DUSUK
    assert Siddet.agirliktan(1) is Siddet.DUSUK


def test_siddet_siralama_ve_etiket():
    # 0 = en ağır (V1 SEVERITY_ORDER uyumu)
    assert Siddet.KRITIK < Siddet.YUKSEK < Siddet.ORTA < Siddet.DUSUK
    assert Siddet.KRITIK.etiket == "KRİTİK"
    assert Siddet.DUSUK.etiket == "DÜŞÜK"


def test_haber_kaynak_skora_girmez():
    # Basın haberi skora katılmaz (V1 ilkesi)
    assert KAYNAK_GUVENILIRLIK[KaynakTipi.HABER] == 0.0
    assert KAYNAK_GUVENILIRLIK[KaynakTipi.KAP] == 1.0
    assert KAYNAK_GUVENILIRLIK[KaynakTipi.DERECELENDIRME] < 1.0


def test_varliklar_kurulur():
    f = Firma(canonical_id="c1", unvan="Test A.Ş.", vkn="1234567890")
    assert f.unvan_varyantlari == []          # default factory izole
    kk = KaynakKaydi(id="kap:1", firma_id="c1", kaynak_tipi=KaynakTipi.KAP,
                     orijinal_kimlik="1", cekim_zamani=datetime(2026, 1, 1),
                     kaynak_url="http://x")
    s = Sinyal(firma_id="c1", kategori_id="iflas", kategori="İflas",
               siddet=Siddet.KRITIK, agirlik=10, tarih=datetime(2026, 1, 1),
               kaynak_kaydi_id=kk.id, kaynak_tipi=KaynakTipi.KAP,
               gerekce="'iflas' ifadesi")
    assert s.iyilesme is False
    assert s.kaynak_kaydi_id == "kap:1"
