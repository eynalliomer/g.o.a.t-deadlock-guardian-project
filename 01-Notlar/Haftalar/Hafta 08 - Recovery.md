---
tags: [deadlock-guardian, hafta]
hafta: 8
durum: tamamlandı
---
# Hafta 8: Recovery (Kurtarma)

**Amaç:** Process sonlandırma, kaynak geri alma, en düşük maliyetli kurbanın seçilmesi, SAFE'e dönüş.

## Yapılacaklar
- [x] Birer birer process sonlandırma (her adımdan sonra tespit tekrar çalışır)
- [x] Kaynak geri alma (preemption) ve rollback
- [x] Maliyet formülüyle kurban seçimi, starvation önlemi
- [x] Senaryoda otomatik (`recover`) ve elle (`terminate`, `preempt`) kurtarma olayları
- [x] Arayüzde kurtarma seçenekleri tablosu (önerilen işaretli) ve uygulanan kurtarma
- [x] Kurtarmadan sonra sistemin tekrar güvenli duruma döndüğünün gösterilmesi
- [x] Testler

## Hafta sonu hedefi
Çalışan kurtarma modülü.

> [!note] Bu hafta kapsam dışı
> Kurtarma seçeneğini arayüzde düğmeyle canlı seçmek hafta 9'daki arayüz kararına (PyQt mı, web mi) bağlı. Şimdilik seçim senaryo dosyasında yapılıyor.

## Uygulama notları

### 1) İki yöntem (Silberschatz 8.8)
| Yöntem | Nasıl? | Sonuç |
|---|---|---|
| **Process sonlandırma** (birer birer) | Kurban sonlandırılır, tespit tekrar çalışır; deadlock sürüyorsa bir sonraki kurban | Process ölür, yaptığı iş kaybolur |
| **Kaynak geri alma** (preemption) | Kurbanın bir kaynağı alınıp bekleyene verilir | Process yaşar ama **geri sarılır** (rollback) |

"Hepsini birden sonlandır" yöntemi seçilmedi: kesin çözer ama gereksiz yere çok iş kaybettirir.

### 2) Kurban seçimi: maliyet (karar: 2026-09-27)
> **maliyet = öncelik × 10 − serbest bırakılan birim × 2 + kurban seçilme sayısı × 5**

- **Öncelik** (senaryoda `priority`, varsayılan 1): önemli process pahalıdır, korunur.
- **Serbest bırakılan birim:** çok kaynak serbest bırakan seçenek ucuzdur, deadlock'u çözme ihtimali yüksektir. Sonlandırmada process'in elindeki bütün birimler, geri almada yalnızca alınan kaynağın birimleri sayılır.
- **Kurban seçilme sayısı** (`victim_count`): sık kurban seçilen process pahalılaşır → **starvation önlenir**.
- **Eşitlikte** geri alma sonlandırmadan önce gelir: process yaşamaya devam eder.

Katsayılar `src/recovery.py`'nin başında üç sabit olarak duruyor.

### 3) Modelde yaptığımız basitleştirmeler
- **Rollback:** Kaynağı geri alınan process, o kaynağı almadan önceki noktaya geri sarılmış sayılır; tekrar ihtiyacı olursa yeniden ister. Diğer kaynakları ve bekleyen istekleri onda kalır.
- **Sonlandırma:** Process önce bütün bekleme kuyruklarından çıkar (bırakılan kaynak ona geri verilmesin diye), sonra elindeki her şeyi bırakır; `release` bırakılanları bekleyenlere dağıtır. Durumu `TERMINATED` olur, Banker's hesabına katılmaz, yeni olay alamaz.
- Yalnızca **birinin beklediği** kaynağı geri almak seçenek olarak sunulur; kimsenin beklemediği kaynağı almak deadlock'u çözmez.

### 4) `src/recovery.py`
- `option_cost()`, `make_option()`: maliyet ve seçenek oluşturma
- `recovery_options()`: deadlock'taki processler için bütün seçenekler, en ucuzu başta
- `terminate()`, `preempt()`, `apply_option()`: seçeneği uygulama
- `recover()`: en ucuzu uygula → tespiti tekrarla → deadlock bitene kadar sür. Döngü her zaman biter: kurtarma sırasında kimse yeni kaynak istemediği için her adımda ya bir bekleyen karşılanır ya da bir kaynak boşa çıkar.

### 5) Senaryo ve arayüz
```json
{"action": "recover"}
{"action": "terminate", "process": "P2"}
{"action": "preempt", "process": "P2", "resource": "R2"}
```
- Deadlock olan adımda mor **"Kurtarma seçenekleri"** tablosu: her seçenek, maliyeti, önerilen ✅.
- Kurtarma adımında yeşil **"Uygulanan kurtarma"** kutusu; olay kaydında `RECOVERY` satırı (kurtarmanın sonuçlarından önce).
- Sonlandırılan process: gri kart, grafta soluk kesikli daire.

`scenarios/hafta8_recovery.json` (P1 önceliği 2, P2 önceliği 1):
```
LOW → LOW → HIGH → HIGH → CRITICAL → MEDIUM → MEDIUM → LOW → MEDIUM → LOW → LOW
```
Deadlock'ta en ucuz seçenek "Geri al: R2, sahibi P2" (maliyet 8). Kurtarmadan sonra Banker's tekrar güvenli sıra buluyor, iki process de işini bitiriyor. Bu, final demo akışının tamamı: **normal → risk artışı → deadlock → tespit → recovery → güvenli durum**.

### 6) Yol boyunca düzeltilenler
- Olay kaydında `RECOVERY` satırı kurtarmanın sonuçlarından sonra yazılıyordu; `recover()`'a `on_apply` parametresi eklenerek karar önce kaydedildi.
- İlk senaryoda P1 işini bitirirken önce R1'i bırakıyordu ve risk bir an HIGH'a çıktı. **Banker's haklıydı:** P1, elinde R2 varken Max'ına göre R1'e yeniden ihtiyaç duyabilirdi ve R1 P2'ye geçmişti. Senaryo sırası düzeltildi.

### 7) Testler
80 test, hepsi geçiyor (65 önceki + 15 yeni) — `tests/test_week8_recovery.py`: maliyet formülü, seçenekler ve sıralama, önceliğin korunması, sonlandırma, geri alma, starvation önlemi, 2 ve 3 processli deadlock'un çözülmesi, Banker's'ın sonlandırılanı saymaması, senaryoda otomatik ve elle kurtarma, sonlandırılan process'in yeni olay alamaması.

← [[00-Genel/11 Haftalık Plan]]
