# -*- coding: utf-8 -*-
"""Altın regresyon seti — motor.siniflandir (V1 test_golden.py'den taşındı).

V1'in 24 vakasından 23'ü metin-tabanlı motora uyarlandı. Dışarıda bırakılan tek
vaka: "finansal rapor gecikmesi" — bu, metinde anahtar kelime içermez; yayın
tarihi ile dönem sonu arasındaki aritmetiğe dayanır ve connector-seviyesi
zenginleştirmedir (ilgili connector eklendiğinde ayrıca test edilecek).
"""
from sinyal_v2.motor import siniflandir


def _yuzey(title, summary=""):
    return f"{title} | {summary}" if summary else title


# (açıklama, title, summary, derin_metin, beklenen kategori | "IYILESME" | None)
GOLDEN = [
    ("MKK gerceklesmeyen itfa", "Merkezi Kayıt Kuruluşu A.Ş. Duyurusu",
     "Gerçekleşmeyen İtfa/Kupon/Getiri Ödemesi", "", "temerrut"),
    ("gozalti pazari", "Borsa İstanbul A.Ş. Duyurusu",
     "Borçlanma Araçlarının Gözaltı Pazarı'na Alınması", "", "yakin_izleme"),
    ("yakin izleme alinma", "Pazar Değişikliği",
     "Payların Yakın İzleme Pazarına Alınması", "", "yakin_izleme"),
    ("dunya bankasi yaptirim", "Özel Durum Açıklaması (Genel)",
     "Dünya Bankası Grubu Tarafından Uygulanan Yaptırım Hakkında", "", "regulator"),
    ("nisab erteleme", "Genel Kurul İşlemlerine İlişkin Bildirim",
     "Asgari Toplantı Nisabının Sağlanamaması Nedeni ile Ertelenen GK", "", "yonetim"),
    ("tedbir uygulanmasi", "Borsa İstanbul A.Ş. Duyurusu",
     "Yatırım Aracı Bazında Tedbir Uygulanması", "", "piyasa_tedbir"),
    ("MARTI kredi yapilandirma", "Özel Durum Açıklaması (Genel)",
     "Denizbank ve Deniz Fact. Kredi Yapılandırmaları Protokol Görüşmeleri Hk.",
     "", "yapilandirma"),
    ("SASA covenant", "Özel Durum Açıklaması (Genel)",
     "PTA Yatırımı kredilerinin raporlanması hakkında", "", "yapilandirma"),
    ("KONTR likidite (derin)", "Özel Durum Açıklaması (Genel)", "Güncel Durum",
     "nakit akışındaki bozulma ve likidite sıkışıklığı yaşanmaktadır", "temerrut"),
    ("VESTL FYY", "Özel Durum Açıklaması (Genel)",
     "Finansal Yeniden Yapılandırma Başvurusu Hakkında", "", "yapilandirma"),
    ("FENER UEFA limit", "Özel Durum Açıklaması (Genel)",
     "UEFA Sürdürülebilirlik Talimatı Kapsamında Limit Aşımı Hakkında", "", "regulator"),
    ("GM yrd ayrilma", "Özel Durum Açıklaması (Genel)",
     "Genel Müdür Yardımcısının ayrılması", "", "yonetim"),
    ("YKBNK TGA satisi", "Özel Durum Açıklaması (Genel)",
     "Tahsili Gecikmiş Alacak Portföyü Alımı-İhale", "", "varlik_satisi"),
    ("VIOP vade acilmamasi", "VİOP Diğer Duyurular",
     "Payına dayalı vadeli işlem sözleşmelerinde yeni vade aylarının işleme açılmaması",
     "", "yakin_izleme"),
    ("rating dusurme (derin)", "Kredi Derecelendirme Notu", "",
     "kredi notunu BBB'den BB'ye düşürmüştür, görünüm negatif", "derecelendirme"),
    ("YIP cikis = iyilesme", "Pazar Değişikliği",
     "Payların Yakın İzleme Pazarı'ndan çıkarılarak Ana Pazar'a alınması", "", "IYILESME"),
    ("konkordato sona erdi = RISK", "Özel Durum Açıklaması",
     "Konkordato mühleti sona erdi, iflas süreci başladı", "", "iflas"),
    ("varlik SATIMI varyanti", "Maddi Duran Varlık Satımı",
     "Nurol Tower Ofis Satışı", "", "varlik_satisi"),
    ("sirketin uyarilmasi", "Şirketin Uyarılması", "Şirketin uyarılması", "", "regulator"),
    ("ipotek tesisi", "Özel Durum Açıklaması (Genel)",
     "Kredi Teminatı Kapsamında İpotek Tesis Edilmesi", "", "varlik_satisi"),
    ("sube kapanisi", "Özel Durum Açıklaması (Genel)", "Şube Kapanışı Hakkında",
     "", "faaliyet"),
    ("rutin kupon = temiz", "Pay Dışında Sermaye Piyasası Aracı İşlemleri",
     "TRF ISIN Kodlu Finansman Bonosunun 3. Kupon Ödemesi", "", None),
    ("rutin GK daveti = temiz", "Genel Kurul İşlemlerine İlişkin Bildirim",
     "2025 Yılı Olağan Genel Kurul Toplantısı Daveti", "", None),
]


def test_golden_regresyon():
    hatalar = []
    for ad, title, summary, deep, beklenen in GOLDEN:
        r = siniflandir(_yuzey(title, summary), deep)
        bulunan = (None if r is None
                   else ("IYILESME" if r.iyilesme else r.kategori_id))
        if bulunan != beklenen:
            hatalar.append(f"{ad}: beklenen={beklenen} bulunan={bulunan}")
    assert not hatalar, "Altın vaka hataları:\n" + "\n".join(hatalar)


def test_golden_vaka_sayisi():
    # V1'in 24 vakasından 23'ü (rapor gecikmesi connector-seviyesi → hariç)
    assert len(GOLDEN) == 23
