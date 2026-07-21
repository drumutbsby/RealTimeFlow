# -*- coding: utf-8 -*-
"""SQLite depo katmanı — kanonik varlıkların kalıcılığı.

PRD §14.4: MVP'de gömülü SQLite yeterlidir; ölçekte PostgreSQL'e geçilir.
Depolama teknolojisi model.py'ye sızmaz — burada izole edilir.

İlke (PRD §11.3): ham kaynak verisi (KaynakKaydi.ham_veri) JSON olarak saklanır
ve üzerine yazılmaz; türetilmiş sinyaller ayrı tabloda tutulur → kanıt zinciri.
"""
from __future__ import annotations

import json
import sqlite3
from datetime import datetime

from .model import (Firma, KaynakKaydi, KaynakTipi, Siddet, Sinyal, SkorAnlik)

_SEMA = """
CREATE TABLE IF NOT EXISTS firma (
    canonical_id     TEXT PRIMARY KEY,
    unvan            TEXT NOT NULL,
    vkn              TEXT,
    mersis           TEXT,
    ticaret_sicil_no TEXT,
    kap_oid          TEXT,
    il               TEXT,
    sektor_nace      TEXT,
    halka_acik       INTEGER DEFAULT 0,
    unvan_varyantlari TEXT DEFAULT '[]'
);
CREATE INDEX IF NOT EXISTS ix_firma_vkn ON firma(vkn);

CREATE TABLE IF NOT EXISTS kaynak_kaydi (
    id              TEXT PRIMARY KEY,
    firma_id        TEXT NOT NULL,
    kaynak_tipi     INTEGER NOT NULL,
    orijinal_kimlik TEXT,
    cekim_zamani    TEXT,
    kaynak_url      TEXT,
    ham_veri        TEXT DEFAULT '{}',
    FOREIGN KEY (firma_id) REFERENCES firma(canonical_id)
);
CREATE INDEX IF NOT EXISTS ix_kk_firma ON kaynak_kaydi(firma_id);

CREATE TABLE IF NOT EXISTS sinyal (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    firma_id        TEXT NOT NULL,
    kategori_id     TEXT,
    kategori        TEXT,
    siddet          INTEGER,
    agirlik         INTEGER,
    tarih           TEXT,
    kaynak_kaydi_id TEXT,
    kaynak_tipi     INTEGER,
    gerekce         TEXT,
    alinti          TEXT,
    kaynak_url      TEXT,
    iyilesme        INTEGER DEFAULT 0,
    guncellik       REAL DEFAULT 1.0,
    FOREIGN KEY (firma_id) REFERENCES firma(canonical_id)
);
CREATE INDEX IF NOT EXISTS ix_sinyal_firma ON sinyal(firma_id);

CREATE TABLE IF NOT EXISTS skor_anlik (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    firma_id      TEXT NOT NULL,
    tarih         TEXT,
    skor          REAL,
    notu          TEXT,
    katman_a      REAL,
    katman_b      REAL,
    guven         REAL,
    model_surumu  TEXT
);
CREATE INDEX IF NOT EXISTS ix_skor_firma ON skor_anlik(firma_id);
"""


class Depo:
    """Kanonik varlık deposu. `yol=":memory:"` testler için bellek-içi DB."""

    def __init__(self, yol: str = ":memory:"):
        self.conn = sqlite3.connect(yol)
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(_SEMA)
        self.conn.commit()

    def kapat(self) -> None:
        self.conn.close()

    # ── Firma ──────────────────────────────────────────────────────────
    def firma_ekle(self, f: Firma) -> None:
        self.conn.execute(
            """INSERT OR REPLACE INTO firma
               (canonical_id, unvan, vkn, mersis, ticaret_sicil_no, kap_oid,
                il, sektor_nace, halka_acik, unvan_varyantlari)
               VALUES (?,?,?,?,?,?,?,?,?,?)""",
            (f.canonical_id, f.unvan, f.vkn, f.mersis, f.ticaret_sicil_no,
             f.kap_oid, f.il, f.sektor_nace, int(f.halka_acik),
             json.dumps(f.unvan_varyantlari, ensure_ascii=False)))
        self.conn.commit()

    def firma_getir(self, canonical_id: str) -> Firma | None:
        r = self.conn.execute("SELECT * FROM firma WHERE canonical_id=?",
                              (canonical_id,)).fetchone()
        return self._firma_cevir(r) if r else None

    def firma_ara_vkn(self, vkn: str) -> Firma | None:
        r = self.conn.execute("SELECT * FROM firma WHERE vkn=?",
                              (vkn,)).fetchone()
        return self._firma_cevir(r) if r else None

    def firmalar(self) -> list[Firma]:
        rows = self.conn.execute("SELECT * FROM firma").fetchall()
        return [self._firma_cevir(r) for r in rows]

    @staticmethod
    def _firma_cevir(r: sqlite3.Row) -> Firma:
        return Firma(
            canonical_id=r["canonical_id"], unvan=r["unvan"], vkn=r["vkn"],
            mersis=r["mersis"], ticaret_sicil_no=r["ticaret_sicil_no"],
            kap_oid=r["kap_oid"], il=r["il"], sektor_nace=r["sektor_nace"],
            halka_acik=bool(r["halka_acik"]),
            unvan_varyantlari=json.loads(r["unvan_varyantlari"] or "[]"))

    # ── KaynakKaydi ────────────────────────────────────────────────────
    def kaynak_kaydi_ekle(self, kk: KaynakKaydi) -> None:
        self.conn.execute(
            """INSERT OR REPLACE INTO kaynak_kaydi
               (id, firma_id, kaynak_tipi, orijinal_kimlik, cekim_zamani,
                kaynak_url, ham_veri) VALUES (?,?,?,?,?,?,?)""",
            (kk.id, kk.firma_id, int(kk.kaynak_tipi), kk.orijinal_kimlik,
             kk.cekim_zamani.isoformat(), kk.kaynak_url,
             json.dumps(kk.ham_veri, ensure_ascii=False)))
        self.conn.commit()

    def kaynak_kaydi_getir(self, kk_id: str) -> KaynakKaydi | None:
        r = self.conn.execute("SELECT * FROM kaynak_kaydi WHERE id=?",
                              (kk_id,)).fetchone()
        if not r:
            return None
        return KaynakKaydi(
            id=r["id"], firma_id=r["firma_id"],
            kaynak_tipi=KaynakTipi(r["kaynak_tipi"]),
            orijinal_kimlik=r["orijinal_kimlik"],
            cekim_zamani=datetime.fromisoformat(r["cekim_zamani"]),
            kaynak_url=r["kaynak_url"], ham_veri=json.loads(r["ham_veri"] or "{}"))

    # ── Sinyal ─────────────────────────────────────────────────────────
    def sinyal_ekle(self, s: Sinyal) -> int:
        cur = self.conn.execute(
            """INSERT INTO sinyal
               (firma_id, kategori_id, kategori, siddet, agirlik, tarih,
                kaynak_kaydi_id, kaynak_tipi, gerekce, alinti, kaynak_url,
                iyilesme, guncellik) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (s.firma_id, s.kategori_id, s.kategori, int(s.siddet), s.agirlik,
             s.tarih.isoformat(), s.kaynak_kaydi_id, int(s.kaynak_tipi),
             s.gerekce, s.alinti, s.kaynak_url, int(s.iyilesme), s.guncellik))
        self.conn.commit()
        return cur.lastrowid

    # ── SkorAnlik (uyarı/değişim tespiti için tarihçe) ─────────────────
    def skor_kaydet(self, s: SkorAnlik) -> int:
        cur = self.conn.execute(
            """INSERT INTO skor_anlik
               (firma_id, tarih, skor, notu, katman_a, katman_b, guven,
                model_surumu) VALUES (?,?,?,?,?,?,?,?)""",
            (s.firma_id, s.tarih.isoformat(), s.skor, s.notu, s.katman_a,
             s.katman_b, s.guven, s.model_surumu))
        self.conn.commit()
        return cur.lastrowid

    def son_skor(self, firma_id: str) -> SkorAnlik | None:
        """Bir firmanın en son kaydedilen skor anlık görüntüsü (yoksa None)."""
        r = self.conn.execute(
            "SELECT * FROM skor_anlik WHERE firma_id=? ORDER BY id DESC LIMIT 1",
            (firma_id,)).fetchone()
        if not r:
            return None
        return SkorAnlik(
            firma_id=r["firma_id"], tarih=datetime.fromisoformat(r["tarih"]),
            skor=r["skor"], notu=r["notu"], model_surumu=r["model_surumu"],
            katman_a=r["katman_a"], katman_b=r["katman_b"], guven=r["guven"])

    def firma_sinyallerini_sil(self, firma_id: str) -> None:
        """Bir firmanın sinyallerini sil — yeniden taramada tekrarı önler
        (kalıcı DB idempotentliği). Skor tarihçesi (skor_anlik) korunur."""
        self.conn.execute("DELETE FROM sinyal WHERE firma_id=?", (firma_id,))
        self.conn.commit()

    def firma_sinyalleri(self, firma_id: str) -> list[Sinyal]:
        rows = self.conn.execute(
            "SELECT * FROM sinyal WHERE firma_id=? ORDER BY siddet, tarih DESC",
            (firma_id,)).fetchall()
        return [Sinyal(
            firma_id=r["firma_id"], kategori_id=r["kategori_id"],
            kategori=r["kategori"], siddet=Siddet(r["siddet"]),
            agirlik=r["agirlik"], tarih=datetime.fromisoformat(r["tarih"]),
            kaynak_kaydi_id=r["kaynak_kaydi_id"],
            kaynak_tipi=KaynakTipi(r["kaynak_tipi"]), gerekce=r["gerekce"],
            alinti=r["alinti"], kaynak_url=r["kaynak_url"],
            iyilesme=bool(r["iyilesme"]), guncellik=r["guncellik"])
            for r in rows]
