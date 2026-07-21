# Sinyalizasyon V2 — Ürün Gereksinim Dokümanı (PRD)

> **Firma Kredi & Karşı Taraf Riski İstihbarat Platformu**
> Büyük KOBİ, kurumsal ve ticari firmaların borçluluk, ödeme performansı ve
> kredi derecelendirme sinyallerini **yalnızca kamuya açık ve yasal** kaynaklardan
> toplayan, firmaları **bilimsel ve açıklanabilir** bir metodolojiyle değerlendiren
> erken uyarı platformu.

| Alan | Değer |
|---|---|
| Doküman durumu | **Taslak v0.2** — olgusal iddialar doğrulandı, inceleme bekliyor |
| Sürüm | 0.2 |
| Tarih | 2026-07-21 |
| Doğrulama | Mevzuat atıfları, veri kaynağı erişilebilirliği ve finansal modeller 2026-07-21'de araştırma ajanlarıyla doğrulandı (bkz. §10, §13 düzeltmeleri) |
| Sahip | umut.okan1@gmail.com |
| Öncül | Sinyalizasyon V1 (KAP Risk İzleme Platformu) — üretimde, korunuyor |
| Kapsam | Türkiye (BIST + BIST-dışı ticari/kurumsal firmalar) |

> ⚠️ **Yasal not:** Bu platform **yatırım tavsiyesi değildir** ve 5411 sayılı Bankacılık
> Kanunu / Findeks anlamında bir **kredi referans/derecelendirme kuruluşu değildir**.
> Yalnızca kamuya açık, yasal olarak erişilebilir verileri derler ve yorumlar.
> Ayrıntı için bkz. [§9 Yasal, Etik ve Uyumluluk Çerçevesi](#9-yasal-etik-ve-uyumluluk-çerçevesi).

---

## İçindekiler

1. [Yönetici Özeti](#1-yönetici-özeti)
2. [Vizyon, Misyon ve Değer Önerisi](#2-vizyon-misyon-ve-değer-önerisi)
3. [Problem Tanımı ve Neden Şimdi](#3-problem-tanımı-ve-neden-şimdi)
4. [V1'den V2'ye Geçiş: Koruma ve Evrim Stratejisi](#4-v1den-v2ye-geçiş-koruma-ve-evrim-stratejisi)
5. [Hedefler ve Başarı Metrikleri](#5-hedefler-ve-başarı-metrikleri)
6. [Kapsam (In / Out of Scope)](#6-kapsam-in--out-of-scope)
7. [Hedef Kullanıcılar, Personalar ve Senaryolar](#7-hedef-kullanıcılar-personalar-ve-senaryolar)
8. [Ürün Gereksinimleri (Fonksiyonel & Fonksiyonel Olmayan)](#8-ürün-gereksinimleri)
9. [Yasal, Etik ve Uyumluluk Çerçevesi](#9-yasal-etik-ve-uyumluluk-çerçevesi)
10. [Veri Kaynakları Kataloğu](#10-veri-kaynakları-kataloğu)
11. [Kanonik Veri Modeli ve Kimlik Eşleştirme](#11-kanonik-veri-modeli-ve-kimlik-eşleştirme)
12. [Risk Sinyalleri ve Kategoriler](#12-risk-sinyalleri-ve-kategoriler)
13. [Bilimsel Skorlama ve Değerlendirme Metodolojisi](#13-bilimsel-skorlama-ve-değerlendirme-metodolojisi)
14. [Sistem Mimarisi](#14-sistem-mimarisi)
15. [Teknoloji Yığını](#15-teknoloji-yığını)
16. [UI/UX ve Raporlama](#16-uiux-ve-raporlama)
17. [Uyarı ve Bildirim Sistemi](#17-uyarı-ve-bildirim-sistemi)
18. [Kalite, Test ve Gözlemlenebilirlik](#18-kalite-test-ve-gözlemlenebilirlik)
19. [Güvenlik ve Gizlilik](#19-güvenlik-ve-gizlilik)
20. [Yol Haritası ve Fazlar](#20-yol-haritası-ve-fazlar)
21. [Riskler ve Azaltım Planı](#21-riskler-ve-azaltım-planı)
22. [Açık Sorular ve Karar Bekleyen Konular](#22-açık-sorular-ve-karar-bekleyen-konular)
23. [Sözlük ve Kısaltmalar](#23-sözlük-ve-kısaltmalar)

---

## 1. Yönetici Özeti

Sinyalizasyon V1, KAP bildirimlerini tarayarak BIST şirketlerinin bozulma
sinyallerini tespit eden, kural tabanlı, tek kaynaklı ve tek dosyalık bir
Streamlit uygulamasıdır. Kanıtlanmış bir çekirdeği (15 risk kategorisi, ağırlıklı
0–100 skor, 24 vakalık altın regresyon seti, KAP dostu dayanıklı veri katmanı)
vardır.

**Sinyalizasyon V2**, bu çekirdeğin ötesine geçerek yalnızca borsa şirketlerini
değil, **büyük KOBİ, kurumsal ve ticari firmaları** kapsayan bir **karşı taraf /
tedarikçi / müşteri kredi riski istihbarat platformu** kurmayı hedefler. Amaç,
internetteki **kamuya açık ve yasal** güvenilir kaynakları (SPK bültenleri,
Resmî Gazete, Ticaret Sicil Gazetesi, JCR Avrasya ve diğer derecelendirme
kuruluşlarının yayımlanan raporları, Basın İlan Kurumu icra/iflas ilanları, KAP,
TCMB makro serileri, kamu ihale yasaklıları vb.) tek bir kanonik firma kimliği
altında birleştirerek, her firma için **açıklanabilir, bilimsel temelli** bir
risk değerlendirmesi üretmektir.

V2 dört sütun üzerine kurulur:
1. **Genişletilmiş veri kaynakları** — KAP-ötesi resmî/güvenilir kaynaklar.
2. **Genişletilmiş risk kalıpları/kategorileri** — kurumsal borçluluk boyutları.
3. **Bilimsel skorlama & analiz motoru** — akademik iflas tahmin modelleri
   (Altman, Ohlson, Merton, Beneish) + sektör normalizasyonu + kalibre ML katmanı.
4. **UI, rapor ve uyarı sistemi** — firma dosyaları, izleme listeleri, otomatik
   uyarılar, denetim izli (audit-trail) raporlar.

Bu doküman ürünün **ne**yini ve **neden**ini tanımlar; **nasıl**ın mühendislik
ayrıntıları fazlara bölünmüş yol haritasında (bkz. §20) somutlaşır.

---

## 2. Vizyon, Misyon ve Değer Önerisi

**Vizyon.** Türkiye'de bir firmayla ticari ilişkiye girmeden önce "bu firma
ödeme/borçluluk açısından ne durumda?" sorusuna, **kamuya açık kanıtlara dayalı,
şeffaf ve bilimsel** bir yanıt veren referans platform olmak.

**Misyon.** Dağınık, yarı-yapılandırılmış ve zor erişilen kamu verilerini tek bir
firma kimliği altında toplayıp normalize etmek; her sinyali kaynağına kadar
izlenebilir (kanıt zincirli) kılmak; ve firmaları açıklanabilir bir skorla
değerlendirerek erken uyarı sağlamak.

**Değer önerisi (kime, ne).**

| Kullanıcı | Acı noktası | V2'nin sunduğu |
|---|---|---|
| Tedarikçi / satıcı (vadeli satış) | Müşterinin batması alacağı yakar | Karşı taraf ödeme riski erken uyarısı |
| Satın alma / tedarik yöneticisi | Kritik tedarikçinin iflası üretimi durdurur | Tedarik zinciri sürekliliği izleme |
| Kredi/finans birimi | Dağınık kaynakları elle taramak yavaş | Tek panelde konsolide risk dosyası |
| Yatırımcı / analist (bilgi amaçlı) | Borsa-dışı firma görünürlüğü düşük | BIST-dışı firmalar için sinyal |
| Denetim / uyum | Kanıtsız iddia riskli | Her sinyalde kaynak + tarih + alıntı |

**Farklılaştırıcılar:** (1) yalnızca yasal/kamusal kaynak; (2) her skorun
açıklanabilir ve kaynağa kadar izlenebilir olması; (3) akademik modellerle
kalibre edilmiş bilimsel skor; (4) BIST-dışı ticari firma kapsamı.

---

## 3. Problem Tanımı ve Neden Şimdi

**Problem.** Bir Türk firmasının mali sağlığına dair sinyaller çok sayıda resmî
ama **birbirinden kopuk** kaynağa dağılmıştır: KAP, Resmî Gazete, Ticaret Sicil
Gazetesi, Basın İlan Kurumu ilanları, derecelendirme kuruluşu raporları, SPK/BDDK
bültenleri, kamu ihale yasaklıları… Bir karar vericinin bunları elle, düzenli ve
firma bazında takip etmesi pratikte imkânsızdır. Sonuç: temerrüt/iflas sinyalleri
**geç** fark edilir.

**Neden V1 yetmiyor.** V1 yalnızca KAP'ı tarar; dolayısıyla yalnızca **borsada
işlem gören** şirketleri kapsar. Türkiye ekonomisinin büyük kısmını oluşturan
halka açık olmayan büyük KOBİ ve ticari firmalar V1'in kör noktasıdır.

**Neden şimdi.** (1) Birçok resmî kaynak son yıllarda çevrim içi sorgu/ilan
arayüzleri sundu (ilan.gov.tr, Ticaret Sicil Gazetesi sorgu, JCR/derecelendirme
kuruluşlarının site yayınları). (2) V1, kural motoru + dayanıklı veri katmanı +
regresyon testi disiplinini kanıtladı; bu iskelet V2'ye taşınabilir. (3)
Açıklanabilir skorlama için olgun akademik modeller (Altman/Ohlson/Merton) mevcut.

---

## 4. V1'den V2'ye Geçiş: Koruma ve Evrim Stratejisi

### 4.1 V1 Korunur (dokunulmaz taban)

- V1 kodu (`kap_risk_app.py`, `kap_risk_tarama.py`, testler, mail modülü) deponun
  kökünde **olduğu gibi çalışır durumda kalır**. Üretimdeki Streamlit uygulaması
  bozulmaz.
- V2 tamamen ayrı bir dizinde (`sinyalizasyon_v2/`) geliştirilir; V1 ile V2
  **birbirinin bağımlılığı değildir**.
- Ek koruma: V1'in son kararlı hâli bir git etiketiyle işaretlenir
  (öneri: `v1-kararli`), böylece geri dönüş noktası nettir. *(Uygulama Faz 0'da.)*

### 4.2 V1'den Devralınan Doğrulanmış Fikirler

V2 sıfırdan başlamaz; V1'in şu tasarım kararları **taşınır**:

- **Kaynak-tek-doğruluk (single source of truth):** kural seti ve veri katmanı
  tek yerde; CLI/UI/servis onu sarar (V1'de CLI'nin çekirdeği sarması gibi).
- **Kanıt zinciri:** her bulguda kaynak metin, tarih, gerekçe ve link tutulur.
- **İyileşme vs. bozulma ayrımı:** kategoriye özgü iyileşme kalıpları (V1'deki
  `IMPROVEMENT_HINTS_BY_CAT` felsefesi) — "sona erdi" gibi ifadelerin bağlamı.
- **Gürültü filtreleme + piyasa-geneli duyuru ayrımı.**
- **Dayanıklı veri çekimi:** hız sınırlayıcı + devre kesici + üstel geri çekilme +
  **sessiz veri kaybını yasaklama** (veri alınamayan firma açıkça işaretlenir).
- **Regresyon disiplini:** her yeni kalıp için altın vaka + birim testi.
- **Güncellik ağırlıklandırma + kategori-içi sönümleme** ile skor şişmesini önleme.

### 4.3 Ana Değişiklik: Tek Kaynaktan Çok Kaynağa

V1'in mimari varsayımı "tek kaynak = KAP"tır. V2'nin merkezî mühendislik
sorunu **çok kaynaklı veriyi tek firma kimliğinde birleştirmektir** (entity
resolution). Bu, §11'de ele alınır ve V2'nin en kritik yeni bileşenidir.

---

## 5. Hedefler ve Başarı Metrikleri

### 5.1 Ürün Hedefleri (Amaç → Anahtar Sonuç)

**A1 — Kapsam:** BIST-dışı ticari firmaları da izleyebilmek.
- AS1.1: İlk sürümde ≥ 3 resmî kaynağın (KAP + Resmî Gazete/İlan + Ticaret Sicil)
  entegre olması.
- AS1.2: Kanonik firma kaydı sayısı ≥ 10.000 (kademeli).

**A2 — Doğruluk:** Sinyaller güvenilir ve düşük yanlış-pozitifli olsun.
- AS2.1: Altın regresyon setinde ≥ %95 doğruluk (V1 disiplininin devamı).
- AS2.2: Skor modelinin geçmiş temerrüt/iflas vakalarında ayırıcılığı (AUC) ≥ 0.75.

**A3 — Erkenlik:** Sinyal, kamuya açık olay anından hızlı yakalansın.
- AS3.1: Yeni bir resmî ilan/bildirimin platforma yansıma süresi (medyan) ≤ 24 saat.

**A4 — Açıklanabilirlik:** Her skor kaynağa kadar izlenebilir olsun.
- AS4.1: Skorun %100'ü kanıt kayıtlarına (kaynak + tarih + alıntı) bağlanabilir.

### 5.2 Ürün KPI'ları

- İzlenen firma sayısı; aktif kaynak sayısı; günlük yeni sinyal sayısı.
- Kaynak başına çekim başarı oranı ve sessiz veri kaybı = 0 hedefi.
- Yanlış-pozitif geri bildirim oranı (kullanıcı işaretlemesiyle).
- Uyarıdan olaya kadar geçen "öncülük süresi" (lead time) dağılımı.

---

## 6. Kapsam (In / Out of Scope)

### 6.1 Kapsam İçi (V2 genel)

- Kamuya açık, yasal kaynaklardan firma düzeyinde risk sinyali toplama.
- Çok kaynaklı veriyi kanonik firma kimliğinde birleştirme.
- Kural tabanlı + model tabanlı hibrit skorlama; açıklanabilir çıktı.
- Firma dosyası, izleme listesi, arama, filtreleme UI'ı.
- Otomatik uyarı (e-posta/panel); zamanlanmış tarama.
- Rapor dışa aktarımı (Excel/PDF/CSV) ve API (ileri faz).

### 6.2 Kapsam Dışı (açıkça)

- ❌ **Kişisel kredi/bireysel skorlama** (Findeks bireysel muadili) — yasal değil,
  hedef değil.
- ❌ **Banka sırrı / müşteri sırrı** kapsamındaki veriler (bkz. §9). **TBB (Türkiye
  Bankalar Birliği) Risk Merkezi** / Findeks **firma** verisi ancak **firmanın kendi
  rızası + lisans** ile alınır; rızasız erişim kapsam dışıdır.
- ❌ **Vergi mahremiyeti** (VUK m.5) kapsamındaki bireysel vergi borcu detayları.
- ❌ Kaynakların kullanım şartlarını (ToS) veya `robots.txt`'yi ihlal eden çekim.
- ❌ Yatırım tavsiyesi, alım/satım sinyali, fiyat hedefi üretme.
- ❌ Doğrulanmamış sosyal medya söylentisini skora katma (yalnızca bilgi notu).

> Kapsam dışı maddeler **kalıcı kırmızı çizgilerdir**; ürün baskısı altında bile
> aşılmaz. Bir kaynağın yasal durumu belirsizse §22 açık sorularına eklenir ve
> hukuki netlik gelene kadar **entegre edilmez**.

---

## 7. Hedef Kullanıcılar, Personalar ve Senaryolar

### 7.1 Personalar

- **P1 — Tedarikçi Kredi Yöneticisi (Ayşe).** Vadeli satış yaptığı 200 müşterinin
  ödeme riskini izler. İhtiyaç: müşteri portföyünü toplu izleme + bozulmada uyarı.
- **P2 — Satın Alma Müdürü (Mert).** Kritik 30 tedarikçinin sürekliliğini izler.
  İhtiyaç: tedarikçi iflas/konkordato/haciz erken uyarısı.
- **P3 — Finans/Hazine Analisti (Deniz).** Karşı taraf limitleri belirler.
  İhtiyaç: konsolide, kanıtlı firma dosyası + skor gerekçesi.
- **P4 — Bağımsız Denetçi / Uyum Uzmanı (Selin).** İşletme sürekliliği ve KYC/UBO
  bağlamında dış kanıt arar. İhtiyaç: kaynağa kadar izlenebilir denetim izi.

### 7.2 Örnek Kullanım Senaryoları

- **S1:** Ayşe müşteri listesini (VKN veya unvan) yükler; platform her firmayı
  eşleştirir, skorlar, D/E notlu olanları uyarı olarak öne çıkarır.
- **S2:** Bir tedarikçi hakkında Basın İlan Kurumu'nda iflas erteleme ilanı çıkar;
  Mert 24 saat içinde panelde ve e-postada uyarı alır, ilanın aslına tıklar.
- **S3:** Deniz bir firmanın dosyasını açar; Altman-Z bölgesi, derecelendirme
  geçmişi (JCR/…), Resmî Gazete'deki ceza kaydı ve KAP sinyalleri tek sayfada,
  her biri tarih ve kaynak linkiyle görünür.

---

## 8. Ürün Gereksinimleri

### 8.1 Fonksiyonel Gereksinimler (FR)

| # | Gereksinim | Öncelik |
|---|---|---|
| FR-1 | Firmayı VKN, MERSİS no, ticaret sicil no veya unvanla arama | Must |
| FR-2 | Çok kaynaklı veriyi tek kanonik firma kaydında birleştirme | Must |
| FR-3 | Her sinyalde kaynak, tarih, alıntı ve orijinal link saklama | Must |
| FR-4 | Kural tabanlı sinyal tespiti (V1 kategorileri + V2 yenileri) | Must |
| FR-5 | Açıklanabilir 0–100 skor + A–E notu üretimi | Must |
| FR-6 | İzleme listesi oluşturma ve toplu tarama | Must |
| FR-7 | Bozulmada otomatik uyarı (panel + e-posta) | Should |
| FR-8 | Excel/PDF/CSV rapor dışa aktarımı | Should |
| FR-9 | Sektör bazlı karşılaştırma ve normalizasyon | Should |
| FR-10 | Geçmişe dönük trend/zaman serisi görünümü | Should |
| FR-11 | Kaynak başına sağlık paneli (çekim başarısı, gecikme) | Should |
| FR-12 | Dış sistemler için okuma API'si | Could (ileri faz) |
| FR-13 | Kullanıcı geri bildirimiyle yanlış-pozitif işaretleme | Could |

### 8.2 Fonksiyonel Olmayan Gereksinimler (NFR)

- **NFR-Yasallık:** Yalnızca izinli/kamusal kaynak; ToS ve `robots.txt`'ye uyum;
  kaynak dostu hız sınırlama (V1 devre kesici felsefesi).
- **NFR-Dayanıklılık:** Bir kaynak çökerse platform çalışmaya devam eder; eksik
  veri **açıkça işaretlenir** (sessiz kayıp yasak).
- **NFR-İzlenebilirlik:** Her türetilmiş değer kaynağına kadar geri sarılabilir.
- **NFR-Tekrarlanabilirlik:** Aynı girdi + aynı kural sürümü → aynı skor
  (deterministik çekirdek; ML katmanı sürümlenir).
- **NFR-Performans:** Tek firma dosyası açılışı ≤ birkaç saniye (önbellekli).
- **NFR-Gizlilik:** KVKK uyumu; veri minimizasyonu; saklama süresi politikası.
- **NFR-Türkçe:** Kullanıcıya dönük tüm metin ve commit mesajları Türkçe.

---

## 9. Yasal, Etik ve Uyumluluk Çerçevesi

> Bu bölüm ürünün **anayasasıdır**; teknik kolaylık uğruna esnetilmez.

### 9.1 Temel İlkeler

1. **Yalnızca yasal ve kamuya açık kaynak.** Bir veri, resmî kurumca kamuya
   açık şekilde yayımlanıyor veya erişime açık sorgu arayüzüyle sunuluyorsa
   kullanılır. Erişim bir yetkiye/rızaya bağlıysa, o yetki/rıza olmadan alınmaz.
2. **Kaynağa saygı (ToS + `robots.txt` + hız).** V1'in KAP dostu davranışı tüm
   kaynaklara genişletilir: hız sınırlama, devre kesici, önbellek. Aşırı yük
   bindirmek hem etik dışı hem sürdürülemezdir.
3. **Doğruluk ve kanıt.** Hiçbir sinyal kaynaksız iddia edilmez; her kayıt
   alıntı + tarih + orijinal link taşır. Yanlış negatif/pozitif geri bildirimi
   düzeltme mekanizması bulunur.
4. **Zarar vermeme.** Bir firmayı yanlış "batıyor" etiketiyle damgalamak gerçek
   ticari zarar verir → skor **olasılıksal ve açıklanabilir** sunulur, kesin
   yargı olarak değil; itiraz/düzeltme yolu tasarlanır.
5. **Yatırım tavsiyesi değildir; kredi referans kuruluşu değildir.** Her ekranda
   ve raporda bu ibare yer alır.

### 9.2 İlgili Mevzuat (dikkate alınacak)

- **6698 sayılı KVKK** — kişisel veri (gerçek kişi tacir, şahıs şirketi ortağı
  vb.) söz konusu olduğunda işleme şartları, aydınlatma, saklama.
- **5411 sayılı Bankacılık Kanunu (m.73 sır saklama; Ek Madde 1 — Risk Merkezi)** —
  banka/müşteri sırrı ve **TBB Risk Merkezi** verisi rızasız alınamaz. (Risk Merkezi
  TCMB'de değil **Türkiye Bankalar Birliği** bünyesindedir; TCMB'nin eski risk
  verileri TBB Risk Merkezi'ne devredilmiştir.)
- **213 sayılı VUK (m.5 vergi mahremiyeti)** — bireysel vergi borcu bilgisi
  mahremdir (kamuya ilan edilen istisnalar hariç, örn. kesinleşmiş vergi/ceza
  ilanları; kanuni ilan yetkisi Hazine ve Maliye Bakanlığı'nda olup uygulamayı
  GİB yürütür).
- **6102 sayılı TTK (m.35 aleniyet)** — Ticaret Sicili ve TTSG kayıtlarının aleniyeti (bu veriler
  kanunen alenîdir → kullanılabilir).
- **Basın İlan Kurumu / ilan mevzuatı** — resmî ilanların (iflas, konkordato,
  ihale, icra) aleniyeti.
- **Kaynakların kendi kullanım şartları** — her kaynak için ayrı değerlendirilir.

### 9.3 Kaynak Onay Süreci (governance)

Her yeni kaynak entegre edilmeden önce bir **Kaynak Değerlendirme Formu**
doldurulur: *ne veriyor, hukuki dayanağı/aleniyeti, erişim yöntemi, ToS durumu,
güncelleme sıklığı, güvenilirlik, kişisel veri içeriyor mu, saklama politikası.*
Kırmızı bayrak varsa entegre edilmez (bkz. §10 renk kodları).

---

## 10. Veri Kaynakları Kataloğu

Kaynaklar **hukuki erişilebilirliğe** göre renk kodludur:

- 🟢 **Yeşil** — kamuya açık ve yasal; entegre edilir.
- 🟡 **Sarı** — kısmen açık / lisans/rıza/dikkat gerektirir; hukuki netlikle.
- 🔴 **Kırmızı** — rızasız/lisanssız erişilemez; **kapsam dışı**.

### 10.1 🟢 Birincil Resmî Kaynaklar (öncelikli entegrasyon)

| Kaynak | Ne sağlar | Erişim | Güncelleme | Not |
|---|---|---|---|---|
| **KAP** (kap.org.tr) | Halka açık şirket bildirimleri | JSON REST endpoint (bkz. not↓) | Gün içi | V1'den devralınır |
| **Resmî Gazete** (resmigazete.gov.tr) | Kamu ihale yasakları, bazı idari yaptırımlar, mevzuat | Aranabilir arşiv (HTML/PDF) | Günlük | Yasaklı listeleri kritik |
| **Basın İlan Kurumu — ilan.gov.tr** | İflas, konkordato, iflas erteleme (İİK 288), icra/izale-i şüyu, ihale ilanları | İlan arama (borçlu/sicil/tarih) | Günlük | BIST-dışı için en değerli sinyal; **WAF/503 riski** → hız sınırlayıcı şart |
| **Ticaret Sicil Gazetesi** (ticaretsicil.gov.tr / TOBB) | Kuruluş, sermaye değişimi, tasfiye, adres/ortaklık değişikliği | Unvan sorgusu ücretsiz; **gazete metni üyelik/giriş ister** | Sürekli | Kanonik kimlik + yapısal olay; toplu/açık API teyit edilmedi → 🟡 sayılmalı |
| **Kamu İhale Kurumu (EKAP) yasaklılar** | İhalelere katılmaktan yasaklananlar (4734/4735/2886) | `ekapv2.kik.gov.tr/sorgulamalar/yasak-sorgulama` veya e-Devlet; ayrıca R.Gazete | Sürekli | İhale yasağı = güçlü sinyal; **WAF/503 riski** |

> **KAP mekanizması notu (V2 için doğrulanacak):** V1, veriyi Next.js sayfasına
> gömülü "flight payload" JSON'undan ayrıştırır. Bağımsız teknik notlar, güncel
> KAP'ın **doğrudan JSON REST endpoint'leri** (`POST /tr/api/disclosure/members/
> byCriteria` — tarih aralığı, ~2000 kayıt/7 gün; `GET /tr/api/notification/
> attachment-detail/{index}`) sunduğunu; PDF indirmelerinin **Java-serialized byte
> array** (`AC ED 00 05` başlıklı) sarmalıyla geldiğini gösteriyor. KAP connector'ı
> yazılmadan önce canlı DOM/endpoint teyidi yapılmalı; hangi yol daha sağlamsa o
> seçilmeli (flight payload hâlâ çalışıyor olabilir ama JSON API tercih edilir).

### 10.2 🟢 Derecelendirme ve Piyasa Kaynakları

| Kaynak | Ne sağlar | Not |
|---|---|---|
| **JCR Avrasya** (jcrer.com.tr) | Yayımlanan derecelendirme notları/raporları | Kamuya açık, giriş yok; notlar **HTML tablo + Excel export** (makine-okunur), ayrıntı PDF; yön tespiti (V1 mantığı) |
| **Diğer yerli derecelendirme kuruluşları** (SPK yetkili listesi) | Yayımlanan notlar/görünüm | Kaynak bazında ToS kontrolü |
| **SPK bültenleri + idari yaptırımlar portalı** (spk.gov.tr) | Haftalık bülten (dönemsel); ceza kayıtları ayrı portal | Bülten: `spk.gov.tr/spk-bultenleri`; cezalar: `idariyaptirimlar.spk.gov.tr` — iki ayrı kaynak |
| **BDDK / EPDK / Rekabet Kurumu kararları** | Sektörel yaptırım/ceza kararları | Kurumsal firmalar için ilgili |
| **TCMB EVDS** (**evds3.tcmb.gov.tr**) | Makro seriler (kur, faiz, sektör borçluluğu) | **Ücretsiz kayıt + API anahtarı (HTTP header) gerekir**; evds2 → evds3'e yönlenir |
| **Google News RSS** | Basında risk temalı haber | V1'deki gibi **skora katılmaz**, yalnızca bilgi |

### 10.3 🟡 Dikkatli / Koşullu Kaynaklar

| Kaynak | Durum |
|---|---|
| **GİB kesinleşmiş vergi/ceza ilanları** | Yalnızca GİB'in **kamuya ilan ettiği** kapsam; VUK m.5 sınırı gözetilir |
| **SGK teşvik/borç ilanları** | Yalnızca kamuya ilan edilen ölçüde |
| **UYAP emsal/karar** | Yalnızca kamuya açık yayımlanan kararlar; kişisel veri anonimleştirmesi |
| **Firma web sitesi / KAP finansal tabloları** | Halka açık firmalarda finansal oranlar (Altman girdisi) buradan; özel firmada tablo yoksa model kısıtlı çalışır |

### 10.4 🔴 Kapsam Dışı Kaynaklar (kırmızı çizgi)

- **TBB (Türkiye Bankalar Birliği) Risk Merkezi / Findeks firma raporu** — yalnızca
  firmanın kendi rızası + lisanslı üyelik ile; rızasız **kesinlikle alınmaz**
  (5411 sayılı Kanun Ek Madde 1).
- **Banka içi / müşteri sırrı verileri** (5411 m.73).
- **Sızdırılmış veri tabanları, kaçak kaynaklar, ToS ihlali gerektiren scraping.**
- **Bireysel vergi mahremiyeti** kapsamındaki veriler.

### 10.5 Kaynak Kalite Katsayısı

Her kaynağa bir **güvenilirlik ağırlığı** atanır (resmî kurum > derecelendirme
kuruluşu > basın). Skorda kaynak güvenilirliği çarpan olarak kullanılır; böylece
"resmî ilan" ile "haber" aynı ağırlıkta değildir.

---

## 11. Kanonik Veri Modeli ve Kimlik Eşleştirme

### 11.1 Neden Kritik

V2'nin en zor mühendislik problemi: aynı firma KAP'ta "SASA POLYESTER SANAYİ
A.Ş.", Ticaret Sicil'de bir MERSİS no, ilan.gov.tr'de bir başka unvan varyantıyla
geçer. Bunları **tek kanonik kimlikte** birleştirmek (entity resolution) tüm
platformun temelidir.

### 11.2 Kanonik Anahtarlar (öncelik sırası)

1. **VKN** (Vergi Kimlik No) — mümkünse birincil anahtar.
2. **MERSİS No** — Ticaret Sicil evreninde birincil.
3. **Ticaret Sicil No + Sicil Müdürlüğü.**
4. **KAP MKK Member OID** (halka açıklar için, V1'den).
5. Fallback: **normalize edilmiş unvan** (V1'in `norm()` + şirket-adı sadeleştirme
   mantığı genişletilerek) + il/adres benzerliği ile olasılıksal eşleştirme.

### 11.3 Çekirdek Varlıklar (kavramsal şema)

```
Firma (canonical_id, vkn, mersis, unvan, unvan_varyantlari[], sektor_nace,
       il, sicil_no, halka_acik?, kaynak_baglari[])
   └─< Kaynak_Kaydi (id, firma_id, kaynak_tipi, orijinal_kimlik, ham_veri,
                     cekim_zamani, kaynak_url)
   └─< Sinyal (id, firma_id, kategori, siddet, agirlik, tarih, kaynak_kaydi_id,
               alinti, gerekce, iyilesme?, guvenilirlik)
   └─< Finansal_Veri (id, firma_id, donem, gelir, aktif, ozkaynak, ... )  [varsa]
   └─< Skor_Anlik (id, firma_id, tarih, skor, not, model_surumu, aciklama[])
   └─< Olay_Zaman_Serisi (firma_id, tarih, skor)  [trend için]
```

**İlke:** ham kaynak verisi **asla üzerine yazılmaz**; her çekim
sürümlenir/zaman damgalanır. Türetilmiş her değer bir `Kaynak_Kaydi`'na bağlanır
(NFR-İzlenebilirlik).

### 11.4 Eşleştirme Kalitesi

- Kesin anahtar (VKN/MERSİS) → **kesin eşleşme**.
- Bulanık eşleşme → **güven skoru** ile; eşik altı eşleşmeler "doğrulama bekliyor"
  kuyruğuna düşer, sessizce birleştirilmez (yanlış birleştirme = yanlış sinyal).

---

## 12. Risk Sinyalleri ve Kategoriler

### 12.1 V1'den Devralınan 15 Kategori (temel)

İflas/Tasfiye/Konkordato (10), Temerrüt/Ödeme (10), Yakın İzleme/Kotasyon (9),
İhaleye Fesat/Yolsuzluk/Adli (9), Finansal Yeniden Yapılandırma (8),
Denetçi Görüşü/Süreklilik (8), Kredi Notu Kötüleşmesi (7), İcra/Haciz (7),
Regülatör Cezası (7), Faaliyet/Üretim (5), Yönetim/Genel Kurul (5),
Varlık Satışı/Teminat (4), Kârlılık/Temettü (4), Dava/Tahkim (4),
Piyasa Tedbirleri (3).

> Bu kategoriler ve ağırlıkları V1 regresyon setiyle korunur; **gerekçesiz
> değiştirilmez** (CLAUDE.md kuralı V2'ye taşınır).

### 12.2 V2'de Eklenen Yeni Boyutlar (BIST-dışı odaklı)

| Yeni kategori | Kaynak | Neden |
|---|---|---|
| **İflas/Konkordato İlanı (resmî ilan)** | ilan.gov.tr | BIST-dışı firmada en güçlü sinyal |
| **İcra/İhale (izale-i şüyu, satış ilanı)** | ilan.gov.tr | Aktif haciz/tasfiye göstergesi |
| **Kamu İhale Yasağı** | EKAP / R.Gazete | Kamu ile iş yapamama → gelir şoku |
| **Sicil Olayı: sermaye azaltımı / tasfiye girişi / tür değişikliği** | TTSG | Yapısal bozulma sinyali |
| **Ortaklık/Yönetim Değişim Kümesi** | TTSG | Ani kontrol değişimi risk işareti |
| **Derecelendirme Yön/Görünüm (çok kuruluşlu)** | JCR + diğerleri | V1 yön mantığının çok-kaynaklı hâli |
| **Vergi/SGK kamu ilanı** (🟡) | GİB/SGK ilan | Yalnızca yasal ilan kapsamı |
| **Sektör-Görece Bozulma** | TCMB + finansal | Firma, sektör ortalamasından ne kadar sapmış |

### 12.3 Sinyal Tasarım Kuralları (V1 disiplini)

- Her yeni kalıp için **hem birim testi hem altın vaka** eklenir.
- İyileşme kalıpları kategoriye özgüdür (bağlamsız "sona erdi" kabul edilmez).
- Gürültü ve piyasa-geneli duyuru ayrımı korunur.
- Kaynak güvenilirliği ağırlığı sinyale çarpan olarak uygulanır (§10.5).

---

## 13. Bilimsel Skorlama ve Değerlendirme Metodolojisi

"Bilimsel değerlendirme" hedefi, skoru sezgisel ağırlık toplamından çıkarıp
**literatürdeki iflas/temerrüt tahmin modelleriyle** kalibre etmeyi gerektirir.

### 13.1 İki Katmanlı Hibrit Skor

**Katman A — Olay/Sinyal Skoru (kural tabanlı, V1 evrimi).**
Kamuya açık olaylardan (ilan, ceza, not düşüşü) gelen ağırlıklı, güncellik
çarpanlı, kategori-içi sönümlemeli skor. Deterministik ve açıklanabilir.

**Katman B — Finansal/İstatistiksel Skor (model tabanlı, finansal veri varsa).**
Halka açık veya finansal tablosu erişilebilir firmalarda akademik modeller:

- **Altman Z-Score ailesi** — **orijinal Z (1968)** imalat + **piyasa değeri**
  gerektirir (halka açık). Halka kapalı firmalarda **Z' (defter değerli varyant)**;
  imalat-dışı ve **gelişen piyasa** için **Z'' + 3.25 sabitli EMS varyantı**
  (Altman'ın Türkiye dâhil gelişen piyasalar için önerdiği biçim). BIST-dışı özel
  firmada varsayılan **Z'/Z''** olmalıdır; orijinal Z kullanılmaz.
- **Ohlson O-Score** — lojistik temelli iflas **olasılığı** (0–1). Finansal
  tabloya ek olarak **ülkeye özgü fiyat endeksi girdisi** gerektirir (SIZE
  değişkeni GSYH deflatörü içerir → Türkiye için **TÜİK GSYH deflatörü** ile
  ölçeklenir; ABD dolar ölçeği doğrudan kullanılmaz).
- **Merton Distance-to-Default** — **piyasa verisi zorunlu** (hisse piyasa değeri +
  volatilite) + borç yapısı → **yalnızca halka açık** firmalara uygulanır. Düşük
  likidite/seyrek işlem gören hisselerde volatilite gürültülüdür; çıktı güven
  aralığıyla sunulur.
- **Beneish M-Score** — **kazanç/tablo manipülasyonu** kırmızı-bayrağı; **iflas
  modeli DEĞİLDİR**. İflas skoruna doğrudan ağırlık olarak **eklenmez**; ayrı bir
  "kazanç kalitesi" sinyali olarak konumlanır. İki dönemlik finansal tablo ister.
- **Piotroski F-Score** — 0–9 arası **finansal sağlamlık/kalite** ölçüsü (iflas
  olasılığı değil). İki dönemlik veri ister; piyasa verisi gerekmez.

> **Taban gereksinim:** *Tüm* modeller finansal tablo ister (Merton dâhil, borç
> yapısı için). **Piyasa verisi yalnızca Merton ve orijinal Altman Z-1968 için**
> zorunludur; Z'/Z'', Ohlson, Beneish ve Piotroski piyasa verisi olmadan yalnız
> tablodan hesaplanır ve bu yüzden halka kapalı firmalara uygulanabilir.
>
> **Gelişen piyasa uyarısı:** Tüm katsayılar ABD verisiyle (1960'lar–1990'lar)
> kalibre edilmiştir; BIST için gelişen-piyasa varyantları tercih edilir ve
> ideal olarak yerel veriyle **yeniden kalibre** edilir. Yüksek enflasyon
> muhasebesi (TMS 29) ve düşük raporlama kalitesi yanlış sınıflandırmayı artırır.

Finansal veri yoksa (özel firma, tablo yok) Katman B devre dışı kalır; sistem
bunu **açıkça belirtir** ("skor yalnızca olay verisine dayanıyor").

### 13.2 Birleştirme (fusion)

Nihai skor, iki katmanın **güvenilirlik-ağırlıklı** birleşimidir; veri
yeterliliği düşükse belirsizlik bandı geniş gösterilir. Her firma skoru bir
**güven aralığı / veri yeterlilik rozeti** ile sunulur (az veri → düşük güven).

### 13.3 Sektör Normalizasyonu

Ham oranlar NACE sektör kohortuna göre z-normalize edilir; "yüksek borç" bir
sektörde normal, başka sektörde alarmdır. TCMB sektör bilançoları referans.

### 13.4 Açıklanabilirlik (zorunlu)

- Her skor için **katkı dökümü**: hangi sinyal/oran kaç puan ekledi.
- Kara-kutu ML kullanılacaksa yanında **SHAP benzeri katkı açıklaması** zorunlu;
  açıklanamayan model üretime alınmaz (NFR-İzlenebilirlik).

### 13.5 Doğrulama / Backtest

- **Altın vaka seti** (V1'den genişletilmiş) — kural katmanı için regresyon.
- **Tarihsel olay backtest'i** — geçmişte batmış/konkordato ilan etmiş firmalarda
  modelin olay öncesi uyarı verip vermediği (lead-time, AUC, precision/recall).
- **Kalibrasyon** — tahmini olasılık ile gerçekleşme oranının uyumu (reliability
  diagram). Model sürümlenir; her sürüm test kartıyla belgelenir.

> **Skor ağırlıkları ve model parametreleri gerekçesiz/testsiz değiştirilmez.**
> Bu, V1'in en sıkı kuralının V2'ye taşınmış hâlidir.

---

## 14. Sistem Mimarisi

### 14.1 Katmanlı Boru Hattı (pipeline)

```
[Kaynaklar] → 1) Toplama (Ingestion)     : kaynak-özel connector'lar, hız sınırlı
            → 2) Ayrıştırma (Parse)       : ham → yapılandırılmış kayıt
            → 3) Kimlik Eşleştirme        : kanonik firma id'ye bağlama
            → 4) Normalize + Depolama     : sürümlü, kaynağa izlenebilir
            → 5) Sinyal Motoru            : kural tabanlı sınıflandırma
            → 6) Skorlama                 : Katman A + B fusion
            → 7) Sunum                    : UI / Rapor / Uyarı / API
```

### 14.2 Connector Soyutlaması

Her kaynak, ortak bir arayüzü uygulayan bir **connector**'dır:
`cek() → ham kayıtlar`, `ayristir() → normalize kayıt`, `saglik() → durum`.
V1'in KAP veri katmanı ilk connector olarak yeniden paketlenir. Yeni kaynak
eklemek = yeni connector yazmak (çekirdek değişmez).

Ortak altyapı (V1'den genelleştirilir): küresel hız sınırlayıcı, devre kesici,
üstel geri çekilme, önbellek (kapanmış dönem süresiz / güncel dönem TTL'li),
başarısızlık = açık işaret (sessiz kayıp yok).

### 14.3 Çalışma Modları

- **Toplu (batch):** zamanlanmış tam/artımlı tarama (gecelik).
- **İsteğe bağlı (on-demand):** kullanıcı bir firmayı açınca taze çekim.
- **(İleri faz) akış:** yeni ilan/bildirim yayımlandıkça yakın-zamanlı işleme.

### 14.4 Depolama

MVP'de dosya/gömülü DB (SQLite) yeterli olabilir; ölçeklendikçe Postgres.
Ham veri (kanıt) ayrı, türetilmiş skor ayrı saklanır. Tasarım kararları §22'de
açık; MVP'de en yalın kalıcı çözüm seçilir.

---

## 15. Teknoloji Yığını

V1 ile uyum ve düşük sürtünme önceliklidir:

- **Dil:** Python 3.13 (V1 ile aynı).
- **UI (MVP):** Streamlit (V1 sürekliliği); ölçeklenince ayrı bir web katmanı
  (FastAPI + modern front-end) değerlendirilir — §22.
- **Veri işleme:** pandas; ağır ETL gerekirse polars değerlendirilir.
- **Çekim:** requests + (gerekirse) HTML/PDF ayrıştırıcılar (lxml/BeautifulSoup,
  pdfplumber) — V1 saf `requests`'i korur, yeni kaynak ihtiyacına göre eklenir.
- **Depolama:** SQLite (MVP) → PostgreSQL (ölçek).
- **Modelleme:** numpy/scipy; ML gerekirse scikit-learn; açıklanabilirlik için
  SHAP. Modeller sürümlenir.
- **Test:** pytest (V1 disiplini) + altın regresyon + backtest kartları.
- **Rapor:** openpyxl (Excel, V1'den) + PDF üretimi (ileri faz).

> Her yeni bağımlılık gerekçelendirilir; V2'nin `requirements.txt`'i V1'den
> **ayrı** tutulur (izolasyon).

---

## 16. UI/UX ve Raporlama

### 16.1 Ana Ekranlar

1. **Arama / Firma Bulma** — VKN/MERSİS/unvanla arama, eşleşme güveni gösterimi.
2. **Firma Dosyası (360° görünüm):**
   - Üst şerit: kanonik kimlik, sektör, skor + not + **güven rozeti**.
   - Skor katkı dökümü (hangi sinyal kaç puan).
   - Zaman çizelgesi: tüm olaylar (ilan, ceza, not, KAP) tarih sıralı, kaynak
     linkli.
   - Finansal panel (varsa): Altman-Z bölgesi, oran trendleri.
   - İyileşme sinyalleri ayrı bölümde (V1 felsefesi).
3. **İzleme Listesi / Portföy** — toplu skor tablosu, sıralama, filtre, "yeni
   bozulma" işareti (V1'in "önceki taramaya göre yeni" özelliğinin evrimi).
4. **Kaynak Sağlık Paneli** — kaynak başına çekim başarısı, gecikme, son güncelleme;
   sessiz kaybı görünür kılar.

### 16.2 Raporlama

- **Excel** (V1 biçimlendirme mirası): yönetici özeti + bulgular + kaynak dökümü +
  metodoloji sayfası.
- **PDF firma dosyası** (ileri faz): denetim/paylaşım için kanıtlı tek-firma raporu.
- **CSV** dışa aktarım.
- Her raporda **"yatırım tavsiyesi değildir" + metodoloji + kaynak listesi**.

### 16.3 UX İlkeleri

- Skor asla gerekçesiz gösterilmez (tıkla → kanıt).
- Belirsizlik dürüstçe gösterilir (az veri → düşük güven, geniş band).
- Türkçe, sade, karar-odaklı.

---

## 17. Uyarı ve Bildirim Sistemi

- **Tetikleyiciler:** izleme listesindeki bir firmanın notunun kötüleşmesi; yeni
  KRİTİK/YÜKSEK sinyal; iflas/konkordato/haciz ilanı; kamu ihale yasağı.
- **Kanallar:** panel içi bildirim + e-posta (V1'deki `kap_rapor_mail.py`
  altyapısı genelleştirilir); ileri fazda webhook/Slack.
- **Zamanlama:** gecelik toplu tarama sonrası özet; kritik olaylarda ara uyarı.
- **Gürültü kontrolü:** eşik + tekrar bastırma (aynı olay tek uyarı); kullanıcı
  hassasiyet ayarı (yalnızca D/E, veya tüm değişimler).
- **İçerik:** her uyarı olayı kaynağına linkler; "neden uyarıldım" açıklaması.

---

## 18. Kalite, Test ve Gözlemlenebilirlik

- **Birim testleri (pytest):** her connector'ın ayrıştırıcısı; her sinyal kuralı.
- **Altın regresyon seti:** V1'in 24 vakası taşınır + V2 kaynakları için yeni
  vakalar; CI'da her PR'da yeşil olması zorunlu (CLAUDE.md DoD).
- **Backtest kartları:** skor modeli sürümleri için tarihsel doğrulama raporu.
- **Eşleştirme testleri:** kimlik eşleştirme precision/recall ölçümü.
- **Gözlemlenebilirlik:** kaynak başına çekim başarı oranı, gecikme, son başarı
  zamanı; sessiz veri kaybı = 0 hedefi panelde izlenir.
- **Veri kalite kontrolleri:** aykırı değer, boş alan, çelişki (aynı firma iki
  kaynakta çelişkili) tespiti ve işaretleme.

---

## 19. Güvenlik ve Gizlilik

- **Veri minimizasyonu:** yalnızca risk değerlendirmesi için gerekli alanlar.
- **Erişim kontrolü:** çok kullanıcı olursa rol tabanlı yetki; izleme listeleri
  kullanıcıya özel.
- **Sır yönetimi:** e-posta/servis kimlik bilgileri ortam değişkeninde (`${ENV}`),
  depoya asla yazılmaz (V1 `.gitignore` disiplini genişletilir).
- **Denetim izi:** kimin hangi firmayı sorguladığı/dışa aktardığı loglanır
  (uyum ve kötüye kullanım önleme).
- **Saklama politikası:** kaynak verisi için saklama süresi; KVKK gereği kişisel
  veri barındıran kayıtlarda silme/anonimleştirme prosedürü.
- **Kişisel/yerel çıktıları commit etme yasağı** (V1 kuralı korunur).

---

## 20. Yol Haritası ve Fazlar

Her faz **çalışan, test edilmiş, gösterilebilir** bir artışla biter (V1 DoD).

### Faz 0 — Temel ve Koruma *(kısa)*
- V1'i etiketle (`v1-kararli`) ve dokunulmaz bırak.
- `sinyalizasyon_v2/` iskeleti: paket yapısı, ayrı `requirements.txt`, test
  altyapısı, connector arayüzü sözleşmesi, kanonik veri modeli şeması.
- V1 KAP veri katmanını ilk **connector** olarak yeniden paketle (davranış aynı,
  regresyon yeşil).
- **Çıktı:** boş ama sağlam iskelet + KAP connector + geçen testler.

### Faz 1 — Çok Kaynaklı Toplama + Kimlik Eşleştirme *(çekirdek)*
- 2–3 yeni 🟢 connector: Basın İlan Kurumu (ilan.gov.tr), Ticaret Sicil Gazetesi,
  Resmî Gazete/EKAP yasaklılar.
- Kanonik firma kaydı + kimlik eşleştirme (VKN/MERSİS kesin + bulanık fallback).
- Kaynağa izlenebilir depolama (SQLite).
- **Çıktı:** bir firmayı çok kaynaktan tek dosyada görebilme.

### Faz 2 — Genişletilmiş Sinyaller + Kural Motoru *(risk kalıpları)*
- V2 yeni kategorileri (§12.2) + kaynak-özel ayrıştırma.
- İyileşme/gürültü/piyasa-geneli disiplininin çok kaynağa taşınması.
- Altın vaka setinin genişletilmesi.
- **Çıktı:** çok kaynaklı, açıklanabilir sinyal akışı.

### Faz 3 — Bilimsel Skorlama *(analiz motoru)*
- Katman A (olay skoru) olgunlaştırma; Katman B (Altman/Ohlson/Merton) finansal
  veri olan firmalar için; fusion + sektör normalizasyonu + güven bandı.
- Backtest ve kalibrasyon kartları.
- **Çıktı:** kalibre, açıklanabilir 0–100 skor + güven rozeti.

### Faz 4 — UI, Rapor, Uyarı *(deneyim)*
- Firma dosyası 360° ekranı, izleme listesi/portföy, kaynak sağlık paneli.
- Excel/PDF rapor; e-posta/panel uyarı sistemi.
- **Çıktı:** uçtan uca kullanılabilir platform (MVP tam).

### Faz 5 — Ölçek ve Açılım *(ileri)*
- Postgres'e geçiş, akış işleme, okuma API'si, çok kullanıcı/rol, daha fazla
  kaynak; opsiyonel modern web front-end.

> Fazlar arasında sıra korunur ama kaynaklar **paralelleştirilebilir** (her
> connector bağımsız). Öncelik, en yüksek sinyal değeri olan 🟢 kaynaklardadır.

---

## 21. Riskler ve Azaltım Planı

| Risk | Etki | Azaltım |
|---|---|---|
| Kaynak yapısı değişir (site/HTML) | Çekim kırılır | Connector izolasyonu + sağlık paneli + hızlı testler |
| Kimlik eşleştirme hatası (yanlış firma birleşimi) | Yanlış sinyal → itibar zararı | Kesin anahtar önceliği; bulanık eşleşme eşiği + doğrulama kuyruğu |
| Yasal belirsizlik (bir kaynak) | Uyum riski | §9.3 kaynak onay süreci; belirsizse entegre etme |
| Yanlış-pozitif firmayı damgalar | Gerçek ticari zarar | Olasılıksal + açıklanabilir skor; itiraz/düzeltme yolu; güven bandı |
| Kaynağa aşırı yük | Engellenme/etik ihlal | V1 hız sınırlayıcı+devre kesici genişletilir |
| Özel firmada finansal veri yok | Model kısıtlı | Katman A tek başına + "az veri" rozeti; sessiz varsayım yok |
| Kapsam şişmesi (scope creep) | Gecikme | Faz disiplini; MVP kırmızı çizgileri |
| Model aşırı-uyum (overfit) | Sahte güven | Backtest + kalibrasyon + sürümleme + regresyon |

---

## 22. Açık Sorular ve Karar Bekleyen Konular

1. **Depolama:** MVP'de SQLite yeterli mi, yoksa baştan Postgres mi? (Öneri:
   SQLite ile başla.)
2. **UI:** Streamlit'te mi kalınsın yoksa Faz 4'te FastAPI + modern front-end mi?
   (Öneri: MVP Streamlit, ölçekte ayrış.)
3. **Kimlik eşleştirme kaynağı:** VKN↔unvan eşlemesi için birincil referans hangi
   kaynak olacak (Ticaret Sicil mi, ayrı bir resmî firma indeksi mi)?
4. **Finansal veri kapsamı:** Katman B başlangıçta yalnızca halka açıklarla mı
   sınırlı (KAP finansalları), yoksa özel firma tablosu erişimi aranacak mı?
5. **JCR/derecelendirme çekimi:** ToS izin veriyor mu, hangi kaynaklar yayınlanan
   notu makine-okur biçimde sunuyor?
6. **Hedef kullanıcı ilk sürüm:** yalnızca kişisel/tekil kullanım mı, yoksa çok
   kullanıcılı mı (bu, güvenlik/rol kapsamını belirler)?
7. **Coğrafi/ölçek sınırı:** yalnızca "büyük KOBİ+kurumsal+ticari" tanımının
   operasyonel eşiği ne (ör. ciro/çalışan filtresi var mı)?

> Bu sorular Faz 0/1 kararlarını etkiler; her biri ilgili faza girmeden önce
> netleştirilir.

---

## 23. Sözlük ve Kısaltmalar

- **KAP** — Kamuyu Aydınlatma Platformu.
- **VKN** — Vergi Kimlik Numarası.
- **MERSİS** — Merkezî Sicil Kayıt Sistemi numarası.
- **TTSG** — Türkiye Ticaret Sicili Gazetesi.
- **EKAP** — Elektronik Kamu Alımları Platformu.
- **JCR Avrasya** — SPK yetkili kredi derecelendirme kuruluşu.
- **NACE** — ekonomik faaliyet sınıflandırması.
- **Entity Resolution** — farklı kaynaklardaki kayıtları tek gerçek varlığa eşleme.
- **Altman Z / Ohlson O / Merton DD / Beneish M / Piotroski F** — akademik
  finansal sağlık / iflas tahmin / manipülasyon skorları.
- **Katman A / Katman B** — olay tabanlı (kural) ve finansal (model) skor katmanları.
- **Connector** — tek bir kaynağı çeken/ayrıştıran izole modül.
- **Kanıt zinciri** — bir sinyalin kaynağına (link+tarih+alıntı) kadar izlenebilirliği.

---

> **Sonraki adım:** Bu PRD onaylandıktan sonra **Faz 0** (iskelet + V1 koruma +
> KAP connector'ın yeniden paketlenmesi) uygulanır. Açık sorular (§22) Faz 0/1
> kararlarını etkilediğinden, uygulamaya geçmeden önce en az 1–4 numaralı sorular
> netleştirilmelidir.
