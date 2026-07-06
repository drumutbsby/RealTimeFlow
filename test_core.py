# -*- coding: utf-8 -*-
"""Çekirdek mantık testleri — ağ erişimi gerektirmez.

Çalıştırma:  python test_core.py   (veya: pytest test_core.py)
"""
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kap_risk_app as app  # noqa: E402

M = {"hisse": "TST", "unvan": "TEST SANAYİ A.Ş.", "oid": "abc123"}


def _b(title, summary="", pub="01.06.2026 10:00:00"):
    return {"title": title, "summary": summary,
            "companyTitle": "TEST SANAYİ A.Ş.", "publishDate": pub,
            "disclosureIndex": 1}


def test_flight_parser():
    # geçerli iç içe dizi (kaçışlı flight biçimi)
    page = ('önek \\"data\\":[{\\"disclosureBasic\\":'
            '{\\"disclosureIndex\\":42,\\"relatedList\\":[1,2]}}] sonek')
    out = app.extract_flight_array(page)
    assert isinstance(out, list) and out[0]["disclosureBasic"][
        "disclosureIndex"] == 42
    # veri bloğu hiç yok → None (kısıtlanmış yanıt)
    assert app.extract_flight_array("herhangi bir sayfa") is None
    # bozuk JSON → None ("temiz şirket" sanılmamalı)
    assert app.extract_flight_array('\\"data\\":[{BOZUK}]') is None
    # kesik yanıt (dizi kapanmıyor) → None
    assert app.extract_flight_array('\\"data\\":[{\\"a\\":1}') is None
    # boş ama geçerli dizi → [] (gerçekten bildirim yok)
    assert app.extract_flight_array('\\"data\\":[]') == []


def test_rating_direction():
    # başlıkta düşürme + nötr detay → KRİTİK yakalanmalı (probe birleşik)
    r = app.classify(_b("Kredi Derecelendirme Notunun Düşürülmesi"), M,
                     "kuruluşumuz hakkında genel bilgilendirme")
    assert r is not None and r["kategori_id"] == "derecelendirme"
    assert r["siddet"] == "KRİTİK"
    # teyit → risk değil
    assert app.classify(_b("Kredi Derecelendirme Notu"), M,
                        "notu teyit etmiştir, görünüm durağan") is None
    # yön belirsiz (yüzey) → DÜŞÜK uyarı
    r2 = app.classify(_b("Kredi Derecelendirme Notu"), M, "")
    assert r2 is not None and r2["siddet"] == "DÜŞÜK"


def test_improvement_category_scoped():
    # ağır sinyal, genel "sona erdi" kalıbıyla MASKELENMEMELİ
    r = app.classify(_b("Özel Durum Açıklaması",
                        "Konkordato mühleti sona erdi, iflas süreci başladı"),
                     M)
    assert r is not None and not r["iyilesme"] and r["kategori_id"] == "iflas"
    # kategoriye özgü gerçek iyileşme tanınmalı
    r2 = app.classify(_b("Pazar Değişikliği",
                         "Payların Yakın İzleme Pazarı'ndan çıkarılarak "
                         "Ana Pazar'a alınması"), M)
    assert r2 is not None and r2["iyilesme"]
    # soruşturmanın sonlandırılması → iyileşme
    r3 = app.classify(_b("Açıklama",
                         "Rekabet Kurumu soruşturmasının sonlandırılması"), M)
    assert r3 is not None and r3["iyilesme"]


def test_recency_and_grades():
    assert app.recency_factor(datetime.now()) == 1.0
    assert app.recency_factor(datetime.min) == app.RECENCY_FLOOR
    assert app.grade_for_score(0)[0] == "A"
    assert app.grade_for_score(19)[0] == "B"
    assert app.grade_for_score(45)[0] == "D"
    assert app.grade_for_score(70)[0] == "E"


def test_norm_and_shortname():
    assert app.norm("Yakın İzleme Pazarı'ndan") == "yakin izleme pazarindan"
    assert app.company_short_name("İŞ BANKASI A.Ş.") == "İŞ BANKASI"
    assert app.company_short_name(
        "KONTROLMATİK TEKNOLOJİ ENERJİ VE MÜHENDİSLİK A.Ş.") == "KONTROLMATİK"


if __name__ == "__main__":
    fails = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"OK   {name}")
            except AssertionError as exc:
                fails += 1
                print(f"FAIL {name}: {exc}")
    print(f"\n{fails} başarısız")
    sys.exit(1 if fails else 0)
