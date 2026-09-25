---
tags: [deadlock-guardian, hafta]
hafta: 6
durum: tamamlandı
---
# Hafta 6: Risk Analizi (Banker's Algorithm)

**Amaç:** Banker's Algorithm ile güvenli durum kontrolü, istek öncesi uyarı.

## Yapılacaklar
- [x] Need = Max − Allocation hesabı
- [x] Güvenlik algoritması (güvenli mi + güvenli sıra), Silberschatz 8.6.3.1
- [x] Kaynak isteği algoritması (SAFE / UNSAFE / WAIT), Silberschatz 8.6.3.2
- [x] Senaryolarda Max bildirimi (`processes` bölümü)
- [x] Her istekten önce değerlendirme, arayüzde ve konsolda uyarı
- [x] Kitap örneğiyle birebir doğrulama ve testler

## Hafta sonu hedefi
Güvenli/güvensiz durum uyarıları.

> [!note] Bu hafta kapsam dışı
> Low/Medium/High/Critical risk seviyeleri hafta 7'ye ait. Bu hafta sistem güvensiz isteği yalnızca **uyarır, engellemez** (plan engellemeyi istemiyor).

## Uygulama notları

### 1) Kavramlar
| Tablo | Anlamı |
|---|---|
| `Available` | Her kaynaktan boşta kaç birim var |
| `Max` | Process'in en fazla ne isteyebileceği (baştan bildirilir) |
| `Allocation` | Process'in şu an elinde olan |
| `Need = Max − Allocation` | En kötü durumda daha ne kadar isteyebileceği |

**Güvenli durum:** Processlerin öyle bir sırası (güvenli sıra) var ki, her biri sırası geldiğinde `Need`'inin tamamını alıp bitirebiliyor.

### 2) Tespit ile Banker's aynı döngüyü kullanıyor
| | Tespit (hafta 4) | Banker's (hafta 6) |
|---|---|---|
| Talep tablosu | `Request` (şu an beklediği) | `Need` (en kötü durumda isteyebileceği) |
| Soru | Şu an deadlock var mı? | İleride deadlock olabilir mi? |

Bu yüzden Work/Finish döngüsü `detect_deadlock`'tan `run_to_completion(work, demand, allocation, finished)` adında ortak bir fonksiyona çıkarıldı (DRY). Hafta 4 testleri bu refactor'dan sonra değişmeden geçti.

### 3) `src/bankers.py`
- `compute_need()`: Need tablosu
- `is_safe()`: (güvenli mi, güvenli sıra)
- `check_request()`: kitaptaki üç adım:
  1. İstek > Need ise **hata** (process Max'ını aşamaz)
  2. İstek > Available ise **WAIT**
  3. İsteği vermiş gibi yap → güvenli mi? **SAFE / UNSAFE**

  Girdileri değiştirmiyor, kopyalar üzerinde çalışıyor (testle doğrulandı).

### 4) Kitap örneğiyle doğrulama (Silberschatz 8.6.3.3)
5 process, A=10, B=5, C=7. Testler kitabın cevaplarını birebir veriyor:
- Başlangıç güvenli, sıra ⟨P1, P3, P4, P0, P2⟩
- P1'in (1,0,2) isteği → SAFE
- Ardından P4'ün (3,3,0) isteği → WAIT, P0'ın (0,2,0) isteği → UNSAFE

**Öğrendiğimiz:** İlk testte P0'ın isteğini kitabın başlangıç durumuna göre sınadık ve kod "güvenli" dedi. Elle hesaplayınca kod haklıydı: kitap bu isteği **P1'in isteği verildikten sonraki** durumda değerlendiriyor. Aynı istek sistemin durumuna göre güvenli de güvensiz de olabilir; Banker's isteğe değil, bütün sisteme bakar.

### 5) Simülasyona bağlama
- Senaryo JSON'una opsiyonel `processes` bölümü eklendi:
  ```json
  "processes": [{"name": "P1", "max": {"R1": 1, "R2": 1}}]
  ```
- **Karar:** Max JSON'da bildiriliyor, ilk istekte değil. Kitaptaki kural da böyle: process sisteme girerken Max'ını bildirir. Max bildiren processler baştan sistemde sayılıyor, çünkü güvenlik hesabı henüz hiçbir şey istememiş olsalar bile onların gelecekteki ihtiyacını hesaba katmak zorunda.
- `processes` bölümü olmayan eski senaryolarda Banker's analizi yapılmıyor (geriye dönük uyumluluk, testle doğrulandı).
- `run_scenario.py` her `acquire`'dan **önce** `evaluate_acquire()` çağırıyor.
- Arayüz: ikinci bir 🏦 şerit (güvenli sıra / GÜVENSİZ), güvensiz istekte kırmızı uyarı, process kartlarında Max ve Need.

### 6) Güvensiz ≠ deadlock
- `scenarios/hafta6_guvensiz_durum.json`: klasik deadlock. Banker's sistemi **2. adımda** güvensiz buluyor; deadlock **4. adımda** oluşuyor. Tespit algoritmasından iki adım önce uyarı.
- `scenarios/hafta6_guvensiz_ama_deadlock_yok.json`: 2. adımda güvensiz, P2 R2'yi bırakınca tekrar güvenli; deadlock hiç oluşmuyor.

Kitaptaki ilişki: deadlock ⇒ güvensiz, ama güvensiz ⇏ deadlock. Güvensiz durum, "deadlock'u artık garanti olarak önleyemiyoruz" demek.

```bash
python3 -m src.run_scenario scenarios/hafta6_guvensiz_durum.json
python3 -m src.run_scenario scenarios/hafta6_guvensiz_ama_deadlock_yok.json
open simulation_view.html
```

### 7) Testler
56 test, hepsi geçiyor (41 önceki + 15 yeni):
- `tests/test_week6_bankers.py` (8): Need, kitap örneği (güvenli sıra, SAFE/WAIT/UNSAFE), Max aşımı, girdilerin değişmemesi
- `tests/test_week6_integration.py` (7): max_claim, tablo kurulumu, klasik senaryoda 2. adımda güvensizlik, JSON `processes` bölümü, arayüz uyarısı, eski senaryoların çalışması

← [[00-Genel/11 Haftalık Plan]]
