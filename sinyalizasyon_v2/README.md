# Sinyalizasyon V2

**Firma Kredi & Karşı Taraf Riski İstihbarat Platformu** — büyük KOBİ, kurumsal ve
ticari firmaların borçluluk, ödeme performansı ve kredi derecelendirme sinyallerini
**yalnızca kamuya açık ve yasal** kaynaklardan toplayıp firmaları **bilimsel ve
açıklanabilir** bir metodolojiyle değerlendiren erken uyarı platformu.

> Bu, **Sinyalizasyon V1** (KAP Risk İzleme Platformu — deponun kökünde, üretimde
> ve korunuyor) projesinin devamıdır. V1'e dokunmaz; kendi izole dizininde gelişir.

## Durum

🚧 **Offline analiz çekirdeği tamam (uçtan uca çalışıyor).** PRD + Faz 0/1/2/3 +
orkestrasyon boru hattı hazır: `connector → motor → skor → depo` zinciri sentetik
KAP kayıtlarıyla test edildi. Katman A skorlama, kimlik eşleştirme, kanıt zincirli
SQLite depo çalışır durumda. Testler yeşil (44).

**Katman B + fusion çalışıyor:** Altman Z'' (EMS), Altman Z', Piotroski F
(ajan-doğrulamalı) + Katman A/B güvenilirlik-ağırlıklı birleştirme. Finansal veri
yoksa Katman A tek başına (düşük güven); varsa fusion + yüksek güven.

**Gerçek veri kaynakları (canlı doğrulandı):**
- **JCR Eurasia** derecelendirme — canlı jcrer.com.tr'den 10 gerçek kayıt.
- **KAP üye rehberi** — canlı kap.org.tr'den 1211 gerçek ihraççı (SASA, THYAO…).

**Erişilebilirlik notu (bu ortam):** kap.org.tr, jcrer.com.tr, ticaretsicil.gov.tr
erişilebilir; **ilan.gov.tr ve resmigazete.gov.tr TLS/bağlantı düzeyinde engelli**
(proxy doğrulanabilir sertifika sunmuyor / bağlantı reset). Bu kaynaklar farklı
bir ağ ortamında bağlanmalı.

**Sırada:** KAP disclosure JSON REST endpoint (flight payload kalktı), Ticaret
Sicil connector, kimlik eşleştirmeyi VKN ile zenginleştirme, Beneish M,
Streamlit UI + uyarı sistemi.

## Belgeler

- **[PRD.md](PRD.md)** — Ürün Gereksinim Dokümanı (vizyon, kapsam, veri kaynakları,
  veri modeli, skorlama metodolojisi, mimari, yol haritası).

## Paket yapısı (Faz 0)

```
sinyal_v2/
  model.py             # kanonik varlıklar: Firma, KaynakKaydi, Sinyal, SkorAnlik
  normalize.py         # norm(), unvan_anahtari(), VKN/MERSİS doğrulama + MERSİS→VKN
  eslestirme.py        # kimlik eşleştirme: VKN > MERSİS-VKN > bulanık unvan + eşik
  depo.py              # SQLite depo: firma / kaynak_kaydi / sinyal (kanıt zinciri)
  kurallar.py          # risk kural kataloğu (V1'den taşındı): 15 kategori + kalıplar
  motor.py             # siniflandir(): kaynak-bağımsız metin → SinyalSonucu
  skor.py              # Katman A skorlama: 0–100 + A–E + açıklanabilir katkı dökümü
  finansal.py          # Katman B: Altman Z''/Z', Piotroski F, Ohlson O (hepsi doğrulandı)
  boru.py              # orkestrasyon: firma_isle + kaynak_tarama (kaynak-güdümlü keşif)
  net.py               # kaynağa saygılı HTTP çekim (hız sınırlamalı)
  connectors/
    base.py            # Connector sözleşmesi (cek/ayristir/saglik) + SaglikDurumu
    kap.py             # KAP (V1 flight-payload ayrıştırıcısı taşındı)
    jcr.py             # JCR Eurasia derecelendirme (parser gerçek HTML'e karşı doğrulandı)
tests/                 # pytest — model, normalize, eşleştirme, depo, KAP ayrıştırıcı
```

## Çalıştırma / test

```bash
pip install -r requirements.txt   # + pip install pytest
python -m pytest -q                # sinyalizasyon_v2/ dizininden — 67 test
python tarama.py                   # demo verisiyle uçtan uca risk dosyaları
python tarama.py --jcr             # + JCR Eurasia'dan CANLI derecelendirme taraması
python tarama.py --csv cikti.csv   # sinyalleri CSV'ye de yaz
```

`--jcr` gerçek jcrer.com.tr verisini çeker, kanonik firmalara çözer ve skorlar
(uçtan uca canlı doğrulandı). KAP tarafı hâlâ demo veriyle çalışır (canlı KAP
mekanizması doğrulanınca bağlanacak).

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
