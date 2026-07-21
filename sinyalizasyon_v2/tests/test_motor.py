# -*- coding: utf-8 -*-
"""motor.siniflandir birim testleri (altın set dışı kenar durumlar)."""
from sinyal_v2.model import Siddet
from sinyal_v2.motor import siniflandir


def test_bos_metin_none():
    assert siniflandir("") is None
    assert siniflandir("   ") is None


def test_gurultu_elenir():
    # NOISE_PATTERNS: planlı bakım üretim riski sayılmaz
    assert siniflandir("Planlı Bakım Duruşu Hakkında") is None
    assert siniflandir("Endeks Değişikliği Duyurusu") is None


def test_rating_pozitif_risk_degil():
    # not teyidi / yükseltme → risk değil (None)
    assert siniflandir("Kredi Derecelendirme Notu teyit edildi, görünüm durağan") is None


def test_agirlik_siddet_eslesmesi():
    r = siniflandir("İflas Kararı Hakkında")
    assert r is not None and r.kategori_id == "iflas"
    assert r.siddet is Siddet.KRITIK and r.agirlik == 10


def test_derin_metin_yuzeyde_yoksa_yakalanir():
    # yüzeyde anahtar yok, derin metinde var → ağırlık 1 düşürülür
    r = siniflandir("Özel Durum Açıklaması", "şirket hakkında haciz işlemi başlatıldı")
    assert r is not None and r.kategori_id == "icra"
    assert r.agirlik == 6            # icra ağırlığı 7, derin → 7-1
