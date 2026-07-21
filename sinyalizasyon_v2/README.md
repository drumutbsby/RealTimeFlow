# Sinyalizasyon V2

**Firma Kredi & Karşı Taraf Riski İstihbarat Platformu** — büyük KOBİ, kurumsal ve
ticari firmaların borçluluk, ödeme performansı ve kredi derecelendirme sinyallerini
**yalnızca kamuya açık ve yasal** kaynaklardan toplayıp firmaları **bilimsel ve
açıklanabilir** bir metodolojiyle değerlendiren erken uyarı platformu.

> Bu, **Sinyalizasyon V1** (KAP Risk İzleme Platformu — deponun kökünde, üretimde
> ve korunuyor) projesinin devamıdır. V1'e dokunmaz; kendi izole dizininde gelişir.

## Durum

🚧 **Faz 0 — Planlama.** Şu an yalnızca ürün gereksinim dokümanı (PRD) mevcuttur.

## Belgeler

- **[PRD.md](PRD.md)** — Ürün Gereksinim Dokümanı (vizyon, kapsam, veri kaynakları,
  veri modeli, skorlama metodolojisi, mimari, yol haritası).

## Yol haritası (özet)

| Faz | Kapsam |
|---|---|
| 0 | İskelet + V1 koruma + KAP connector'ın yeniden paketlenmesi |
| 1 | Çok kaynaklı toplama (ilan.gov.tr, Ticaret Sicil, Resmî Gazete) + kimlik eşleştirme |
| 2 | Genişletilmiş risk sinyalleri + kural motoru |
| 3 | Bilimsel skorlama (Altman/Ohlson/Merton + sektör normalizasyonu) |
| 4 | UI, rapor, uyarı sistemi (MVP tam) |
| 5 | Ölçek: Postgres, akış, API, çok kullanıcı |

Ayrıntı için [PRD §20](PRD.md#20-yol-haritası-ve-fazlar).

## İlkeler (V1'den devralınan)

- Yalnızca yasal/kamusal kaynak; kaynağa saygılı çekim (hız sınırlayıcı + devre kesici).
- Sessiz veri kaybı yok — eksik veri açıkça işaretlenir.
- Her sinyal kaynağına kadar izlenebilir (kanıt zinciri).
- Skor ağırlıkları gerekçesiz/testsiz değişmez; her kalıp için regresyon testi.
- **Yatırım tavsiyesi değildir; kredi referans kuruluşu değildir.**
