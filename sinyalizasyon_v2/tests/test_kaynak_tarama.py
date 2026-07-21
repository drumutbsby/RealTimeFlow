# -*- coding: utf-8 -*-
"""boru.kaynak_tarama testleri — kaynak-güdümlü keşif + kimlik eşleştirme."""
import os

from sinyal_v2.boru import kaynak_tarama
from sinyal_v2.connectors.jcr import JcrConnector, derecelendirmeleri_ayristir
from sinyal_v2.depo import Depo
from sinyal_v2.eslestirme import Eslestirici

FIXTURE = os.path.join(os.path.dirname(__file__), "fixtures", "jcr_ornek.html")


def _kayitlar():
    with open(FIXTURE, encoding="utf-8") as fh:
        return derecelendirmeleri_ayristir(fh.read())


def test_kaynak_tarama_firma_kesfi_ve_skor():
    depo, esl, conn = Depo(), Eslestirici(), JcrConnector()
    skorlar = kaynak_tarama(depo, esl, conn, _kayitlar())
    # iki firma keşfedildi
    assert len(depo.firmalar()) == 2
    assert len(skorlar) == 2
    # Negatif görünümlü firma derecelendirme sinyali + skor > 0
    riskli = next(f for f in depo.firmalar() if "RİSKLİ" in f.unvan)
    sinyaller = depo.firma_sinyalleri(riskli.canonical_id)
    assert len(sinyaller) == 1 and sinyaller[0].kategori_id == "derecelendirme"
    assert skorlar[riskli.canonical_id].skor > 0
    # Durağan firma sinyalsiz, skor 0
    saglam = next(f for f in depo.firmalar() if "SAĞLAM" in f.unvan)
    assert depo.firma_sinyalleri(saglam.canonical_id) == []
    assert skorlar[saglam.canonical_id].skor == 0.0


def test_kaynak_tarama_ayni_firma_tekrar_birlesmez():
    # Aynı kayıtları iki kez tara → kimlik eşleştirme yeni firma YARATMAZ
    depo, esl, conn = Depo(), Eslestirici(), JcrConnector()
    kaynak_tarama(depo, esl, conn, _kayitlar())
    kaynak_tarama(depo, esl, conn, _kayitlar())
    assert len(depo.firmalar()) == 2           # hâlâ 2 firma
