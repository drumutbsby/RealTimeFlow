# -*- coding: utf-8 -*-
"""
KAP Risk Tarama — komut satırı sürümü (ince sarmalayıcı)
=========================================================
Kural seti, sınıflandırma ve veri katmanı TEK kaynaktan gelir:
`kap_risk_app.py` çekirdeği. Bu dosya yalnızca komut satırı akışını sağlar;
böylece CLI ile web arayüzü asla sessizce ayrışmaz.

Kullanım:
  python kap_risk_tarama.py                          # varsayılan 10 hisse
  python kap_risk_tarama.py --hisse KONTR,VESTL      # seçili hisseler
  python kap_risk_tarama.py --yil 2023 --derin       # 2023'ten bugüne, derin
"""
import argparse
import csv
import os
import sys
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kap_risk_app as core  # noqa: E402  (kurallar/veri katmanı çekirdekten)


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description="KAP risk taraması (CLI)")
    p.add_argument("--hisse", default=",".join(core.DEFAULT_TICKERS),
                   help="virgülle ayrılmış hisse kodları")
    p.add_argument("--yil", type=int, default=date.today().year - 2,
                   help="tarama başlangıç yılı (varsayılan: 2 yıl önce)")
    p.add_argument("--derin", action="store_true",
                   help="bildirim tam metinleri de taransın")
    p.add_argument("--csv", default="kap_risk_raporu.csv",
                   help="çıktı CSV dosyası")
    args = p.parse_args()

    print("KAP üye rehberi indiriliyor...")
    directory = core.fetch_member_directory()
    wanted = [h.strip().upper() for h in args.hisse.split(",") if h.strip()]
    members = []
    for row in directory.itertuples():
        codes = set(str(row.kodlar).split(","))
        if codes & set(wanted):
            members.append({"hisse": row.hisse, "unvan": row.unvan,
                            "oid": row.oid, "islem": row.islem})
    eksik = [w for w in wanted
             if not any(w in str(row.kodlar).split(",")
                        for row in directory.itertuples())]
    if eksik:
        print("  UYARI - rehberde bulunamadı:", ", ".join(eksik))

    years = tuple(range(args.yil, date.today().year + 1))
    rows = []
    for i, m in enumerate(members, 1):
        print(f"[{i}/{len(members)}] {m['hisse']} — {m['unvan'][:55]}")
        r = core.scan_company(m, years, deep=args.derin)
        print(f"    {r['taranan']} bildirim → {len(r['findings'])} bulgu | "
              f"skor {r['skor']:.0f}/100 ({r['not']}-{r['seviye']})")
        for f in sorted(r["findings"],
                        key=lambda f: core.SEVERITY_ORDER.get(f["siddet"], 9)):
            print(f"      [{f['siddet']:^7}] {f['tarih_str'][:10]} "
                  f"{f['kategori']} | {(f['ozet'] or f['baslik'])[:70]}")
            rows.append({k: f[k] for k in
                         ("hisse", "sirket", "tarih_str", "siddet",
                          "kategori", "baslik", "ozet", "gerekce", "link")})

    with open(args.csv, "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]) if rows else
                           ["hisse", "bulgu"])
        w.writeheader()
        w.writerows(rows)
    print(f"\nToplam {len(rows)} bulgu → {args.csv}")


if __name__ == "__main__":
    main()
