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
from sinyal_v2.rapor import (firma_raporu_metin, portfoy_satiri,
                             portfoy_tablosu, sinyaller_csv)
from sinyal_v2.uyari import uyari_metni, uyari_uret

# Varsayılan izleme listesi (V1'den; gerçek, işlem gören BIST kodları)
IZLEME_LISTESI = ["SASA", "KONTR", "VESTL", "THYAO", "TUPRS", "YKBNK"]


def _finansal_degerlendirme(yol: str) -> None:
    """JSON finansal veriden bilimsel (Katman B) değerlendirme yazdır."""
    import json
    from sinyal_v2.finansal import tum_modeller, veriden_yukle
    from sinyal_v2.rapor import finansal_rapor
    with open(yol, encoding="utf-8") as fh:
        d = json.load(fh)
    cari = veriden_yukle(d.get("cari", {}))
    if cari is None:
        print("HATA — 'cari' altında 8 zorunlu finansal alan gerekli.")
        return
    onceki = veriden_yukle(d.get("onceki", {})) if d.get("onceki") else None
    m = d.get("merton") or {}
    sonuclar = tum_modeller(
        fv=cari, onceki=onceki, gsyh_deflator=d.get("gsyh_deflator"),
        merton_ozkaynak=m.get("piyasa_ozkaynak"),
        merton_vol=m.get("ozkaynak_volatilite"), merton_borc=m.get("borc"))
    print(f"═══ {d.get('unvan', 'Firma')} — finansal değerlendirme ═══")
    print(finansal_rapor(sonuclar))


def _kap_canli(depo: Depo, kodlar: list, bas: str, bit: str,
               derin: bool = False) -> list:
    """Belirtilen BIST kod(lar)ı için KAP'tan CANLI bildirim tara + skorla."""
    mod = " [derin]" if derin else ""
    print(f"═══ KAP canlı tarama ({bas} – {bit}){mod} ═══")
    from sinyal_v2.connectors.kap import uye_rehberi_ayristir
    from sinyal_v2.model import Firma
    try:
        rehber = uye_rehberi_ayristir(net.get(
            "https://www.kap.org.tr/tr/bildirim-sorgu"))
    except Exception as exc:                           # noqa: BLE001
        print(f"  UYARI — KAP üye rehberi çekilemedi: {exc}\n")
        return []
    conn = KapConnector(http_post=net.post_json, http_get=net.get)
    detay_getir = ((lambda ham: conn.detay_metni(ham.get("disclosureIndex")))
                   if derin else None)
    tum, satirlar, uyarilar = [], [], []
    ayrinti = len(kodlar) <= 3           # az firma → tam dosya; çok → tablo
    for kod in kodlar:
        eslesen = [r for r in rehber if kod in r["kodlar"].split(",")]
        if not eslesen:
            print(f"  UYARI — '{kod}' KAP rehberinde bulunamadı")
            continue
        r = eslesen[0]
        firma = Firma(canonical_id=kod.lower(), unvan=r["unvan"],
                      kap_oid=r["oid"], halka_acik=True)
        sonuc = conn.cek({"oid": r["oid"], "bas_tarih": bas, "bit_tarih": bit})
        if not sonuc.saglik.basarili:
            print(f"  UYARI — {kod} bildirimleri çekilemedi: "
                  f"{sonuc.saglik.hata}")
            continue
        skor = firma_isle(depo, conn, firma, sonuc.ham_kayitlar,
                          detay_getir=detay_getir)
        sinyaller = depo.firma_sinyalleri(firma.canonical_id)
        eksik = " [KISMİ VERİ]" if sonuc.saglik.kismi_veri else ""
        # önceki taramaya göre değişim → uyarı (kalıcı DB varsa anlamlı)
        onceki = depo.son_skor(firma.canonical_id)
        u = uyari_uret(onceki, skor)
        if u:
            uyarilar.append(u)
        depo.skor_kaydet(skor)
        print(f"  {kod}: {sonuc.saglik.cekilen_kayit} bildirim → "
              f"skor {skor.skor:.1f} ({skor.notu}){eksik}")
        if ayrinti:
            print(firma_raporu_metin(firma, skor, sinyaller))
            print()
        satirlar.append(portfoy_satiri(kod, r["unvan"], skor, sinyaller))
        tum += sinyaller
    if len(satirlar) > 1:
        print(portfoy_tablosu(satirlar))
    if uyarilar:
        print()
        print(uyari_metni(uyarilar))
    return tum


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
    p.add_argument("--kap", metavar="KODLAR",
                   help="BIST kodları (virgüllü) için KAP'tan CANLI tara, "
                        "ör. --kap SASA,KONTR")
    p.add_argument("--izleme", action="store_true",
                   help="varsayılan izleme listesini KAP'tan canlı tara "
                        f"({','.join(IZLEME_LISTESI)})")
    p.add_argument("--bas", default="2024-01-01", help="KAP başlangıç (YYYY-MM-DD)")
    p.add_argument("--bit", default="2025-12-31", help="KAP bitiş (YYYY-MM-DD)")
    p.add_argument("--derin", action="store_true",
                   help="belirsiz derecelendirme bildirimlerinin detayını "
                        "okuyup yönü belirle (daha yavaş)")
    p.add_argument("--db", metavar="DOSYA",
                   help="kalıcı SQLite DB — önceki taramaya göre uyarı üretir")
    p.add_argument("--finansal", metavar="JSON",
                   help="JSON finansal veriden bilimsel (Katman B) değerlendirme")
    args = p.parse_args(argv)

    if args.finansal:
        _finansal_degerlendirme(args.finansal)
        return 0

    depo = Depo(args.db) if args.db else Depo()
    tum_sinyaller = []

    if args.kap or args.izleme:
        kodlar = (IZLEME_LISTESI if args.izleme else
                  [k.strip().upper() for k in args.kap.split(",") if k.strip()])
        tum_sinyaller += _kap_canli(depo, kodlar, args.bas, args.bit, args.derin)
    else:
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
