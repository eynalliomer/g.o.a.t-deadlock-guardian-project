---
tags: [deadlock-guardian, hafta]
hafta: 4
durum: tamamlandı
---
# Hafta 4: Deadlock Tespiti

**Amaç:** RAG + DFS ile döngü arama, çok örnekli kaynaklar için detection algoritması, raporlama.

## Yapılacaklar
- [x] Mevcut durumdan Resource Allocation Graph (RAG) kurulması
- [x] DFS (üç renk) ile döngü arama
- [x] Çok örnekli kaynaklar için tespit algoritması (Silberschatz 8.7.2)
- [x] Tespit sonucunun raporlanması (`DeadlockReport`)
- [x] Raporun konsolda ve HTML görünümde gösterilmesi
- [x] Birim testleri ve deadlock senaryoları

## Hafta sonu hedefi
Tespit modülü ve birim testleri.

> [!note] Bu hafta kapsam dışı
> Grafın düğüm/ok olarak çizilmesi hafta 5'e (Görselleştirme) ait. Bu hafta tespit sonucu yalnızca durum şeridi ve kart vurgusu olarak gösteriliyor.

## Uygulama notları

### 1) RAG: graf zaten verinin içinde (Silberschatz 8.3.2)
RAG'de iki tür kenar vardır:

| Kenar | Yön | Anlamı | Koddaki karşılığı |
|---|---|---|---|
| İstek kenarı | P → R | P, R'yi bekliyor | `resource.waiting_queue` |
| Atama kenarı | R → P | R'nin bir birimi P'nin elinde | `resource.allocation` |

Yeni bir veri yapısı tutmadık: `build_rag(resources)` grafı her seferinde kaynakların o anki durumundan okuyup `{düğüm: [komşular]}` sözlüğü olarak kuruyor. Böylece graf ile simülasyon asla birbirinden kopmuyor.

### 2) DFS ile döngü arama (üç renk)
- **Beyaz:** hiç ziyaret edilmedi
- **Gri:** şu anki DFS yolunun üstünde (yığında)
- **Siyah:** bitti, buradan döngü çıkmıyor

Gri bir düğüme tekrar ulaşmak = kendi yolumuza geri dönmek = **döngü**. `path[path.index(neighbor):]` yolu döngünün başladığı yerden kesiyor; böylece döngüye yalnızca **bekleyen ama döngünün parçası olmayan** processler (örn. P3) karışmıyor. Siyah düğümler bir daha taranmadığı için karmaşıklık O(V + E).

### 3) Döngü her zaman deadlock değildir → tespit algoritması (Silberschatz 8.7.2)
**Tek örnekli** kaynaklarda döngü = deadlock. **Çok örnekli** kaynaklarda döngü yalnızca *olası* bir deadlock'tur: örneğin R1'in 2 birimi varsa ve biri kimseyi beklemeyen P3'teyse, P3 bitince döngü çözülür.

Bu yüzden `detect_deadlock(resources)` kitaptaki algoritmayı uyguluyor:
1. `Work = Available`. Elinde hiçbir şey olmayan processler `Finish = True` (kimseyi kilitleyemezler).
2. `Finish = False` ve `Request ≤ Work` olan bir process bul → bitireceğini varsay: `Work += Allocation`, `Finish = True`.
3. Bulunamayana kadar tekrarla. `Finish = False` kalanlar **deadlock'ta**.

**Önemli fark:** Döngüye dahil olmayan ama elinde kaynak tutarken döngüdeki bir kaynağı bekleyen process (P3) de asla bitemez. `find_cycle` onu göstermez, `detect_deadlock` gösterir. Hafta 8'de (recovery) bu fark önemli olacak.

### 4) Raporlama: `DeadlockReport` ve `analyze()`
`analyze(resources)` iki algoritmayı birlikte çalıştırıp tek raporda topluyor:
- `deadlocked`: takılı processler (tespit algoritmasından)
- `cycle`: RAG'deki döngü (varsa)
- `summary()`: üç durumdan biri: *deadlock yok* / *döngü var ama deadlock yok* / *DEADLOCK*
- `cycle_path()`: döngüyü `P1 → R2 → P2 → R1 → P1` biçiminde, hep alfabetik en küçük düğümden başlayarak yazar

### 5) Arayüz
`run_scenario.py` her olaydan sonra `analyze()` çağırıyor. `html_view.py` her adımın başına renkli bir **durum şeridi** koyuyor (yeşil / turuncu / kırmızı) ve deadlock'taki processlerin kartlarına **DEADLOCK** etiketi ekliyor. `report` parametresi opsiyonel olduğu için hafta 2'nin `simulation.py`'si değişmeden çalışıyor.

```bash
python3 -m src.run_scenario scenarios/hafta4_deadlock.json
python3 -m src.run_scenario scenarios/hafta4_dongu_deadlock_yok.json
open simulation_view.html
```

### 6) Testler
32 test, hepsi geçiyor (17 önceki + 15 yeni):
- `tests/test_week4_rag.py` (6): kenar kurulumu, döngü var/yok, 2 ve 3 processli döngüler, döngü dışı process
- `tests/test_week4_detection.py` (5): tek/çok örnekli deadlock, döngü var ama deadlock yok, döngüye takılı process
- `tests/test_week4_report.py` (4): rapor alanları, döngü yolu biçimi, "döngü var ama deadlock yok" özeti

← [[00-Genel/11 Haftalık Plan]]
