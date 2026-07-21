# -*- coding: utf-8 -*-
"""KAP üye rehberi parser testi.

Parser CANLI kap.org.tr sayfasına karşı doğrulandı (1211 gerçek ihraççı: SASA,
THYAO, KONTR, TÜPRAŞ… + 178 kodsuz ihraççı). Bu test, gerçek gömülü yapıyı
yansıtan sentetik sayfayla kararlı regresyon sağlar.
"""
from sinyal_v2.connectors.kap import uye_rehberi_ayristir

# KAP sayfasındaki kaçışlı gömülü ihraççı yapısını taklit eden sentetik metin
# (\\" → çalışma zamanında \" — parser önce bunu " yapar).
SENTETIK = (
    'onbilgi ... '
    '{\\"kapMemberOid\\":\\"a1\\",\\"mkkMemberOid\\":\\"ABC123\\",'
    '\\"kapMemberTitle\\":\\"ÖRNEK SANAYİ A.Ş.\\",'
    '\\"stockCode\\":\\"ORN\\",\\"payIslemDurumu\\":\\"1\\"} ara metin '
    '{\\"kapMemberOid\\":\\"a2\\",\\"mkkMemberOid\\":\\"DEF456\\",'
    '\\"kapMemberTitle\\":\\"KODSUZ HOLDİNG A.Ş.\\",'
    '\\"stockCode\\":\\"-\\",\\"payIslemDurumu\\":\\"0\\"} son'
)


def test_rehber_ihraccilari_cikarir():
    rehber = uye_rehberi_ayristir(SENTETIK)
    assert len(rehber) == 2
    kodlu = next(r for r in rehber if r["hisse"] == "ORN")
    assert kodlu["unvan"] == "ÖRNEK SANAYİ A.Ş."
    assert kodlu["oid"] == "ABC123" and kodlu["islem"] == "1"


def test_kodsuz_ihracci_yildizli_etiket():
    rehber = uye_rehberi_ayristir(SENTETIK)
    kodsuz = next(r for r in rehber if r["unvan"].startswith("KODSUZ"))
    assert kodsuz["hisse"].startswith("*")     # kodsuz ihraççı işaretli
    assert kodsuz["oid"] == "DEF456"


def test_bos_sayfa_bos_liste():
    assert uye_rehberi_ayristir("veri yok") == []
