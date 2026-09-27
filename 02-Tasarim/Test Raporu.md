---
tags: [deadlock-guardian, test, rapor]
hafta: 10
tarih: 2026-09-28
---
# Deadlock Guardian: Test Raporu

**Sürüm:** `hafta-10` · **Test aracı:** pytest 9 + pytest-cov · **Python:** 3.14

## 1. Özet

| Ölçüt | Sonuç |
|---|---|
| Toplam test | **127** |
| Geçen / kalan | **127 / 0** |
| Kod kapsamı (satır) | **%99** (787 satırın 783'ü) |
| Bu hafta bulunan ve düzeltilen hata | **5** |
| Sistem testi senaryosu | **5 / 5** beklenen sonucu verdi |

Testleri çalıştırmak:
```bash
python -m pytest tests/ -v                 # bütün testler
python -m pytest tests/ --cov=src          # kod kapsamıyla
```

## 2. Test türleri

| Tür | Neyi test eder? | Projedeki örnek |
|---|---|---|
| **Birim (unit)** | Tek fonksiyon/sınıf | `test_week4_rag.py` (DFS döngü arama), `test_week6_bankers.py` (güvenlik algoritması), `test_week8_recovery.py` (maliyet formülü) |
| **Entegrasyon** | Modüllerin birlikte çalışması | `test_week6_integration.py` (senaryo + Banker's), `test_week9_engine.py` (motor + tespit + kurtarma + geri al) |
| **Sistem** | Uygulamanın baştan sona davranışı | `test_week10_system.py` (senaryo dosyası baştan sona), `test_week9_app.py` (web arayüzünün düğmeleri) |
| **Duman (smoke)** | Program çöküyor mu? | `test_week10_cli.py` (komut satırı araçları) |
| **Regresyon** | Yeni değişikliğin eskiyi bozmaması | Her hafta bütün önceki testler yeniden çalıştırıldı ve geçti |

Test dosyaları haftalara göre ayrılmıştır (`tests/test_weekN_*.py`), böylece her testin hangi aşamada eklendiği bellidir:

| Hafta | Dosyalar | Test |
|---|---|---|
| 2 | `test_week2_simulation.py` | 5 |
| 3 | `test_week3_event_log.py`, `test_week3_multi_instance.py`, `test_week3_scenario_loader.py` | 12 |
| 4 | `test_week4_rag.py`, `test_week4_detection.py`, `test_week4_report.py` | 15 |
| 5 | `test_week5_graph_view.py`, `test_week5_stepper.py` | 9 |
| 6 | `test_week6_bankers.py`, `test_week6_integration.py` | 15 |
| 7 | `test_week7_risk.py` | 9 |
| 8 | `test_week8_recovery.py` | 15 |
| 9 | `test_week9_engine.py`, `test_week9_app.py` | 19 |
| 10 | `test_week10_edge_cases.py`, `test_week10_system.py`, `test_week10_cli.py` | 28 |

## 3. Sistem testleri

Her test üç parçalıdır: **hazırlık** (senaryo dosyası), **eylem** (motorla baştan sona oynatma), **beklenen sonuç**.

| No | Senaryo | Dosya | Beklenen sonuç | Gerçek sonuç | Durum |
|---|---|---|---|---|---|
| 1 | Normal çalışma: processler kaynakları sırayla alıp bırakıyor | `hafta10_normal_calisma.json` | Deadlock yok, risk hep LOW | Risk seyri: 9 adımın hepsi LOW; her istek SAFE | ✅ |
| 2 | Tek deadlock: P1-R1-P2-R2 çapraz istek | `hafta4_deadlock.json` | P1 ve P2 deadlock'ta, risk CRITICAL | Deadlock: P1, P2; risk CRITICAL | ✅ |
| 3 | Çoklu deadlock: iki ayrı döngü | `hafta10_coklu_deadlock.json` | İki döngü ayrı ayrı raporlanıyor | Döngü 1: P1 → R2 → P2 → R1 → P1, Döngü 2: P3 → R4 → P4 → R3 → P3; recovery iki kurtarmayla ikisini de çözdü | ✅ (düzeltme sonrası) |
| 4 | Recovery: deadlock + kurtarma | `hafta8_recovery.json` | Deadlock kalmadı, sistem SAFE | CRITICAL → recovery → güvenli sıra P1 → P2; son risk LOW | ✅ |
| 5 | Döngü var ama deadlock yok | `hafta4_dongu_deadlock_yok.json` | Deadlock yok (en sık yapılan hatayı yakalar) | Risk en fazla MEDIUM, hiç CRITICAL olmadı | ✅ |

**Senaryo 3'te bulunan eksik:** Döngü arama ilk bulduğu döngüde duruyordu; iki bağımsız deadlock olduğunda raporda yalnızca biri görünüyordu. `find_cycles()` eklendi: bir döngü bulununca onun düğümlerini graftan çıkarıp aramayı tekrarlıyor. Rapor, risk nedenleri ve graf çizimi artık bütün ayrık döngüleri gösteriyor.

## 4. Uç durumlar (edge cases)

Uç durumlar testlerden önce elle denendi. Yedi durumdan beşinde hata bulundu, önce hatayı yakalayan test yazıldı (kırmızı), sonra düzeltildi (yeşil).

| # | Durum | Önceki davranış | Sonrası | Değerlendirme |
|---|---|---|---|---|
| 1 | Kaynağın toplam adedinden fazla istek (toplam 1, istek 2) | Process sonsuza kadar bekliyordu ve tespit algoritması bunu görmüyordu | `ValueError`: toplam adetten fazla istenemez | 🐞 Düzeltildi |
| 2 | Negatif miktar (-3) | Toplamı 1 olan kaynakta 4 birim boşta görünüyordu | `ValueError` | 🐞 Düzeltildi |
| 3 | Sıfır miktar | Tabloya boş bir `P1: 0` kaydı ekleniyordu | `ValueError` | 🐞 Düzeltildi |
| 4 | Beklemedeki (WAITING) process yeni istek/bırakma yapıyor | İki kuyrukta birden duruyor, durumu yanlışlıkla READY oluyordu | `ValueError`: bekleyen process bloke durumdadır | 🐞 Düzeltildi |
| 5 | Senaryoda olmayan kaynak (R9) | `AttributeError`, web arayüzünde sayfa çöküyordu | Anlaşılır `ValueError`, arayüzde hata mesajı | 🐞 Düzeltildi |
| 6 | Kendi tuttuğu kaynağı tekrar isteme | Process kendini bekliyor, tespit algoritması onu deadlock'ta buluyor | Değişmedi | ✅ Bilinçli: tekrar girilemeyen (non-reentrant) kilitte gerçek sistemler de böyle kilitlenir |
| 7 | Tutmadığı kaynağı bırakma | Anlaşılır `ValueError` | Değişmedi | ✅ Doğru |
| 8 | Sonlandırılmış process işlem yapıyor | Anlaşılır `ValueError` (hafta 8'den beri) | Değişmedi | ✅ Doğru |
| 9 | Hiç process/kaynak yok | Sorunsuz çalışıyor | Değişmedi | ✅ Doğru |

**Tasarım ilkesi:** Doğrulama, durumu değiştirmeden **önce** yapılıyor. Hatalı bir eylem sistemi yarım bırakmıyor; web arayüzünde durum bozulmadan kırmızı hata mesajı gösteriliyor.

## 5. Kod kapsamı

| Modül | Kapsam | Modül | Kapsam |
|---|---|---|---|
| `detection.py` (tespit) | 100% | `engine.py` (motor) | 100% |
| `bankers.py` (Banker's) | 100% | `graph_view.py` (RAG çizimi) | 100% |
| `risk.py` (risk seviyeleri) | 100% | `scenario_loader.py` | 100% |
| `recovery.py` (kurtarma) | 100% | `state_table.py` | 100% |
| `resource.py` | 100% | `process.py` | 100% |
| `html_view.py` | 100% | `dashboard_view.py` | 100% |
| `app.py` (web) | 98% | `run_scenario.py` | 98% |
| `simulation.py` | 96% | `event_log.py` | 90% |
| **Toplam** | **%99** | | |

Kapsam dışı kalan 4 satır: üç `if __name__ == "__main__":` satırı (program yalnızca komut satırından doğrudan çalıştırıldığında devreye girer) ve `EventLog.__repr__` (hata ayıklama metni).

**Kapsam ölçümü neyi gösterdi:**
1. İlk ölçümde kapsam **%90**'dı; eksik kalan kısım komut satırı araçlarıydı (`run_scenario.main`, hafta 2 demo betiği, durum tablosu). Duman testleri eklendi.
2. İkinci ölçümde kalan satırlar incelendiğinde, bunların hepsinin `__main__` satırı olmadığı görüldü: **web arayüzünün iki güvenlik doğrulaması** (geçersiz process/kaynak adı, 1'den küçük birim), dashboard'daki güvensiz istek uyarısı ve iki görünüm dalı hiç test edilmemişti. Bunlar için 5 test eklendi; doğrulamalar doğru çalışıyordu, ama artık bir testle korunuyor.

## 6. Kitapla doğrulama

Banker's Algorithm, Silberschatz 8.6.3.3'teki örnekle (5 process, A=10, B=5, C=7) birebir doğrulandı: güvenli sıra ⟨P1, P3, P4, P0, P2⟩, P1'in (1,0,2) isteği SAFE, ardından P4'ün (3,3,0) isteği WAIT, P0'ın (0,2,0) isteği UNSAFE. (`test_week6_bankers.py`)

## 7. Bilinen sınırlamalar

- **Heuristic risk seviyeleri:** LOW/MEDIUM eşikleri (%20 boş kaynak) ekip kararıdır, kesin bir garanti vermez.
- **Banker's yalnızca uyarır:** Güvensiz istek engellenmez (plan gereği). Max bildirilmeyen senaryolarda HIGH seviyesi değerlendirilemez.
- **Rollback basitleştirilmiştir:** Kaynağı geri alınan process yalnızca o kaynağı almadan önceki noktaya döner.
- **Kuyruk servisi starvation'a açıktır:** Bekleme kuyruğu karşılanabilen istekleri atlayarak servis eder (hafta 3); büyük istekler sürekli geride kalabilir.
- **Ayrık döngüler:** `find_cycles()` birbirinden ayrık döngüleri bulur; ortak düğüm paylaşan döngüler tek döngü olarak raporlanır. Deadlock'taki processlerin tamamı yine de tespit algoritmasıyla eksiksiz bulunur.
- **Web arayüzü tek kullanıcılıdır:** Durum sunucunun belleğinde tutulur; yerel demo içindir.

← [[00-Genel/11 Haftalık Plan]]
