---
tags: [deadlock-guardian, hafta]
hafta: 7
durum: tamamlandı
---
# Hafta 7: Risk Seviyesi Sistemi

**Amaç:** Low/Medium/High/Critical seviyeleri ve nedenleri.

## Yapılacaklar
- [x] Dört risk seviyesi ve kuralları (ekip kararı)
- [x] Her seviyenin nedenini açıklayan mesajlar
- [x] Her adımdan sonra riskin hesaplanması ve kaydedilmesi (risk seyri)
- [x] Arayüzde risk paneli ve tıklanabilir risk seyri çubuğu
- [x] Testler

## Hafta sonu hedefi
Risk göstergesi ve açıklamalar.

> [!note] Bu hafta kapsam dışı
> Deadlock'tan çıkış (recovery) hafta 8'e ait. Risk paneli, deadlock ve Banker's şeritlerinin tek ekranda sadeleştirilmesi hafta 9'a (arayüz) bırakıldı.

## Uygulama notları

### 1) Neden seviyelere ihtiyaç var?
Banker's yalnızca iki cevap verir: güvenli ya da güvensiz. Tespit algoritması da yalnızca "deadlock var/yok" der. Kullanıcı için asıl faydalı olan "ne kadar tehlikedeyiz ve neden?" sorusunun cevabıdır. Risk seviyeleri bu iki algoritmanın sonucunu ve birkaç basit gözlemi tek bir göstergede birleştiriyor.

Bu bölüm ders kitabında hazır bulunmaz, **projenin kendi tasarımıdır** ve bir **heuristic**'tir (kesin garanti vermeyen ama pratikte işe yarayan kural).

### 2) Kurallar (karar: 2026-09-27)
| Seviye | Koşul |
|---|---|
| **CRITICAL** | Tespit algoritması deadlock buldu |
| **HIGH** | Sistem güvensiz: Banker's güvenli sıra bulamıyor |
| **MEDIUM** | Sistem güvenli, ama bekleyen process var **VEYA** boştaki kaynak toplamın **%20'sinin altında** **VEYA** RAG'de döngü var ama deadlock yok |
| **LOW** | Hiçbiri: "Sistem normal çalışıyor." |

**Verilen kararlar:**
- MEDIUM için "bekleme VEYA az kaynak" seçildi (el kitabındaki "VE" yerine). İki kural ayrı ayrı neden olarak raporlanıyor; demoda LOW → MEDIUM geçişi erken ve net görünüyor.
- Eşik %20 (el kitabındaki değer). Tam %20'de tetiklenmez, çünkü kural "altı". Kodda tek bir sabit: `FREE_RATIO_THRESHOLD = 0.20`.
- Max bildirilmemiş senaryolarda Banker's çalışmadığı için HIGH değerlendirilemez; seviye LOW / MEDIUM / CRITICAL olabilir.

### 3) `src/risk.py`
- `RiskLevel(IntEnum)`: seviyeler karşılaştırılabilir (`LOW < CRITICAL`), en yükseği sıralamayla bulunur.
- `assess_risk(processes, resources)`: her kural tetiklenirse `(seviye, neden)` ekler. Seviye = en yüksek; nedenler en ciddiden başlayarak listelenir.

Örnek neden mesajları:
```
• DEADLOCK: P1, P2 takılı. Döngü: P1 → R2 → P2 → R1 → P1
• Sistem güvensiz: Banker's güvenli sıra bulamıyor.
• P2 bekliyor: R1 (1 birim) şu an P1 elinde.
• Boştaki kaynak az: 0/2 birim (%0).
```

### 4) Risk seyri
`run_scenario.py` her adımdan sonra riski hesaplayıp `risk_timeline` listesine ekliyor. Konsolda:
```
--- Risk Seyri ---
LOW → LOW → HIGH → HIGH → CRITICAL
```
Aynı olaylar, Max bildirimi olmadan (hafta 4 senaryosu): `LOW → LOW → MEDIUM → MEDIUM → CRITICAL`. Fark Banker's'tan geliyor: Max bilinmeyince sistem yalnızca "kaynak azaldı" diyebiliyor, bilinince "güvensiz" diyebiliyor.

### 5) Arayüz
- Sayfanın üstünde **risk seyri**: her adım için renkli bir yuvarlak (yeşil / sarı / turuncu / kırmızı); tıklayınca o adıma gidiyor.
- Her adımın başında **risk paneli**: `RİSK: HIGH` rozeti ve nedenlerin listesi.
- MEDIUM rengi ilk sürümde açık sarıydı, beyaz yazı okunmuyordu; koyulaştırıldı.

```bash
python3 -m src.run_scenario scenarios/hafta6_guvensiz_durum.json
open simulation_view.html
```

### 6) Testler
65 test, hepsi geçiyor (56 önceki + 9 yeni) — `tests/test_week7_risk.py`: seviye sırası, LOW, bekleme ve az kaynakla MEDIUM, tam eşikte LOW, döngü var deadlock yok MEDIUM, güvensiz HIGH, deadlock CRITICAL, senaryoda risk seyri.

← [[00-Genel/11 Haftalık Plan]]
