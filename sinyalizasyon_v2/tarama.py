# -*- coding: utf-8 -*-
"""Sinyalizasyon V2 — komut satırı tarama (gösterim).

Offline analiz çekirdeğini demo verisiyle uçtan uca çalıştırır: her firmayı
işler, risk dosyasını yazdırır, isteğe bağlı CSV üretir.

Kullanım:
  python tarama.py                 # demo firmaların risk dosyaları
  python tarama.py --csv cikti.csv # sinyalleri CSV'ye de yaz

Not: Canlı KAP/ilan.gov.tr connector'ları bağlanınca demo verisi gerçek çekimle
değiştirilecektir (PRD yol haritası).
"""
import argparse
import sys

from sinyal_v2 import net
from sinyal_v2.boru import firma_isle, kaynak_tarama
from sinyal_v2.connectors.jcr import JcrConnector
from sinyal_v2.connectors.kap import KapConnector
from sinyal_v2.demo import demo_veri
from sinyal_v2.depo import Depo
from sinyal_v2.eslestirme import Eslestirici
from sinyal_v2.rapor import firma_raporu_metin, sinyaller_csv


def _jcr_canli(depo: Depo) -> list:
    """JCR Eurasia'dan CANLI derecelendirme çek → firma dosyaları yazdır."""
    print("═══ JCR Eurasia canlı derecelendirme taraması ═══")
    conn = JcrConnector(http_get=net.get)
    sonuc = conn.cek({})
    if not sonuc.saglik.basarili:
        print(f"  UYARI — JCR çekilemedi: {sonuc.saglik.hata}\n")
        return []
    print(f"  {sonuc.saglik.cekilen_kayit} derecelendirme kaydı çekildi.\n")
    esl = Eslestirici(depo.firmalar())
    skorlar = kaynak_tarama(depo, esl, conn, sonuc.ham_kayitlar)
    tum = []
    for fid, skor in sorted(skorlar.items(), key=lambda kv: -kv[1].skor):
        firma = depo.firma_getir(fid)
        sinyaller = depo.firma_sinyalleri(fid)
        if sinyaller:                       # yalnız sinyali olanları göster
            print(firma_raporu_metin(firma, skor, sinyaller))
            print()
        tum += sinyaller
    return tum


def main(argv=None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description="Sinyalizasyon V2 tarama")
    p.add_argument("--csv", help="sinyalleri bu CSV dosyasına yaz")
    p.add_argument("--jcr", action="store_true",
                   help="JCR Eurasia'dan CANLI derecelendirme de tara")
    args = p.parse_args(argv)

    depo = Depo()
    tum_sinyaller = []
    conn = KapConnector()
    for firma, ham in demo_veri():
        skor = firma_isle(depo, conn, firma, ham)
        sinyaller = depo.firma_sinyalleri(firma.canonical_id)
        print(firma_raporu_metin(firma, skor, sinyaller))
        print()
        tum_sinyaller += sinyaller

    if args.jcr:
        tum_sinyaller += _jcr_canli(depo)

    if args.csv:
        with open(args.csv, "w", encoding="utf-8-sig") as fh:
            fh.write(sinyaller_csv(tum_sinyaller))
        print(f"CSV yazıldı: {args.csv}  ({len(tum_sinyaller)} sinyal)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
