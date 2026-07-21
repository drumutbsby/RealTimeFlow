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

from sinyal_v2.boru import firma_isle
from sinyal_v2.connectors.kap import KapConnector
from sinyal_v2.demo import demo_veri
from sinyal_v2.depo import Depo
from sinyal_v2.rapor import firma_raporu_metin, sinyaller_csv


def main(argv=None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description="Sinyalizasyon V2 tarama (demo)")
    p.add_argument("--csv", help="sinyalleri bu CSV dosyasına yaz")
    args = p.parse_args(argv)

    depo = Depo()
    conn = KapConnector()
    tum_sinyaller = []
    for firma, ham in demo_veri():
        skor = firma_isle(depo, conn, firma, ham)
        sinyaller = depo.firma_sinyalleri(firma.canonical_id)
        print(firma_raporu_metin(firma, skor, sinyaller))
        print()
        tum_sinyaller += sinyaller

    if args.csv:
        with open(args.csv, "w", encoding="utf-8-sig") as fh:
            fh.write(sinyaller_csv(tum_sinyaller))
        print(f"CSV yazıldı: {args.csv}  ({len(tum_sinyaller)} sinyal)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
