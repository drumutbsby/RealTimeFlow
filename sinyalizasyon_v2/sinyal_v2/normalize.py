# -*- coding: utf-8 -*-
"""Metin ve kimlik normalize yardımcıları.

İki iş yapar:
  1. Serbest metni (bildirim/ilan başlığı, şirket unvanı) risk kuralı eşleşmesi
     için sadeleştirir — V1'in kanıtlanmış `norm()` mantığının taşınmış hâli.
  2. Kanonik firma kimliklerini (VKN, MERSİS) yapısal olarak doğrular/normalize
     eder — çok kaynaklı kayıtları tek firmaya bağlamanın (entity resolution)
     ilk adımı.

Not: VKN doğrulaması yalnızca YAPISAL/CHECKSUM kontrolüdür; bir numaranın
gerçekten bir firmaya ait olduğunu KANITLAMAZ, yalnızca geçerli biçimde
olduğunu söyler.
"""
import re

# V1'den birebir: TR'ye özgü karakterleri sadeleştirir; kesme işaretleri
# eşleşmeyi bozmasın diye atılır.
_TR_MAP = str.maketrans("çÇğĞıİöÖşŞüÜ", "ccggiioossuu")


def norm(s: str) -> str:
    """Metni kural eşleşmesi için normalize et (küçük harf + TR sadeleştirme)."""
    if not s:
        return ""
    s = re.sub(r"['’`´]", "", s)
    return s.translate(_TR_MAP).lower()


# Unvan sonundaki rutin şirket türü ekleri (eşleştirmede gürültü yapar).
# Sondan yinelemeli temizlenir → 'X SANAYİ VE TİCARET A.Ş.' tüm kuyruğu atar.
_UNVAN_EKLERI = (
    "anonim sirketi", "limited sirketi", "ltd sti", "a s", "ltd", "sti",
    "sanayi", "ticaret", "san", "tic", "ve", "holding", "as", "ao",
)


def unvan_anahtari(unvan: str) -> str:
    """Firma unvanından bulanık eşleştirme için sadeleştirilmiş anahtar üret.

    'SASA POLYESTER SANAYİ A.Ş.' → 'sasa polyester'. Noktalama atılır, rutin
    şirket-türü ekleri sondan YİNELEMELİ temizlenir. Kesin eşleşme (VKN/MERSİS)
    yoksa son çare olarak kullanılır; tek başına birleştirme kararı için
    YETERSİZDİR.
    """
    t = norm(unvan)
    t = re.sub(r"[^\w\s]", " ", t)          # noktalama → boşluk
    t = re.sub(r"\s+", " ", t).strip()
    ekler = sorted(_UNVAN_EKLERI, key=len, reverse=True)
    degisti = True
    while degisti and t:
        degisti = False
        for ek in ekler:
            yeni = re.sub(rf"(^|\s){re.escape(ek)}$", "", t).strip()
            if yeni != t:
                t, degisti = yeni, True
                break
    return t


def _sadece_rakam(s: str) -> str:
    return re.sub(r"\D", "", s or "")


def vkn_gecerli(vkn: str) -> bool:
    """Türk Vergi Kimlik Numarası (10 hane) checksum doğrulaması.

    Algoritma (Gelir İdaresi): ilk 9 hane üzerinden ağırlıklı bir toplam
    hesaplanır, 10. hane kontrol hanesidir.

    ⚠️ DOĞRULANACAK: checksum algoritması Faz 0 doğrulama adımında bilinen
    geçerli VKN örnekleriyle teyit edilmelidir (bkz. test_normalize).
    """
    d = _sadece_rakam(vkn)
    if len(d) != 10:
        return False
    hane = [int(c) for c in d]
    toplam = 0
    for i in range(9):
        gecici = (hane[i] + (9 - i)) % 10
        if gecici != 0:
            gecici = (gecici * pow(2, 9 - i)) % 9
            if gecici == 0:
                gecici = 9
        toplam += gecici
    kontrol = (10 - (toplam % 10)) % 10
    return kontrol == hane[9]


def vkn_normalize(vkn: str) -> str | None:
    """VKN'yi 10 haneli kanonik biçime getir; geçersizse None."""
    d = _sadece_rakam(vkn)
    return d if (len(d) == 10 and vkn_gecerli(d)) else None


def mersis_gecerli(mersis: str) -> bool:
    """MERSİS numarası yapısal kontrolü (16 hane).

    MERSİS no 16 hanedir ve içine VKN'yi gömer (baştaki bazı haneler + VKN).
    Faz 0'da yalnızca uzunluk/rakam kontrolü yapılır; tam checksum/yerleşim
    doğrulaması ileriki fazda eklenecektir.
    """
    d = _sadece_rakam(mersis)
    return len(d) == 16


def mersis_normalize(mersis: str) -> str | None:
    d = _sadece_rakam(mersis)
    return d if len(d) == 16 else None
