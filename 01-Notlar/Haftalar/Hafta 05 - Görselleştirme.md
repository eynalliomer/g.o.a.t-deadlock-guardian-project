---
tags: [deadlock-guardian, hafta]
hafta: 5
durum: tamamlandı
---
# Hafta 5: Görselleştirme

**Amaç:** Graf çizimi, tutma/bekleme kenarları, döngünün vurgulanması.

## Yapılacaklar
- [x] RAG'in her adımda graf olarak çizilmesi (SVG)
- [x] Atama (R → P) ve istek (P → R) kenarlarının ayrı gösterimi
- [x] Çok örnekli kaynaklarda her örneğin nokta olarak gösterimi
- [x] Döngünün ve deadlock'taki processlerin vurgulanması
- [x] Sayfada adım adım gezinme (önceki/sonraki, klavye, tümünü göster)

## Hafta sonu hedefi
RAG ekranı.

> [!note] Bu hafta kapsam dışı
> Deadlock oluşmadan önce uyarı (güvenli/güvensiz durum) hafta 6'ya (Banker's Algorithm) ait.

## Uygulama notları

### 1) Çizim yöntemi: neden elle SVG?
Üç seçenek vardı: Python ile SVG üretmek, Graphviz, JS kütüphanesi (vis.js vb.). **SVG** seçildi:
- Ek kütüphane/kurulum yok, her satır okunabilir ve anlatılabilir.
- Mevcut statik HTML sayfasına doğrudan gömülüyor.
- JS kütüphanesi seçseydik hafta 9'daki arayüz kararını (PyQt mı web mi?) şimdiden vermiş olurduk.

### 2) Yerleşim: RAG iki parçalı (bipartite) bir graftır
RAG'de kenarlar hep process ile kaynak arasındadır; P → P veya R → R kenarı yoktur. Bu yüzden otomatik yerleşim algoritmasına gerek kalmadı: **processler üst sırada, kaynaklar alt sırada**. Bütün oklar iki sıra arasında akıyor, hiçbir kenar bir düğümün içinden geçmiyor. Her sıra yatayda ortalanıyor (`_row_positions`).

Aynı process–kaynak çifti arasında hem atama hem istek olabilir (örn. P, R1'den 1 birim tutarken 1 birim daha bekliyor). Oklar üst üste binmesin diye atama okları 8 px sola, istek okları 8 px sağa kaydırılıyor.

### 3) Gösterim (Silberschatz Şekil 8.4)
| Öğe | Çizim |
|---|---|
| Process | Daire |
| Kaynak | Dikdörtgen; içinde her örnek için bir nokta (dolu = verilmiş, boş = boşta) |
| Atama R → P | Düz ok (birden fazla birimse `×2` etiketi) |
| İstek P → R | Kesikli ok |
| Döngü kenarları | Kalın; deadlock varsa **kırmızı**, döngü var ama deadlock yoksa **turuncu** |
| Deadlock'taki process | Kırmızı dolgu |

**Renk kararı:** İlk sürümde her döngü kırmızıydı. "Döngü var ama deadlock yok" senaryosunda durum şeridi turuncu, graf kırmızı olunca ekran çelişkili görünüyordu. Grafın rengi şeritle aynı olacak şekilde düzeltildi ve bir testle sabitlendi.

Döngüdeki kenarlar `report.cycle` listesinden bulunuyor: ardışık her `(u, v)` çifti (sondan başa dönüş dahil) bir kenar. Çizilen kenar bu kümedeyse vurgulanıyor (`_cycle_edges`).

### 4) Test edilebilir çizim
Her SVG öğesine CSS sınıfı verildi: `node process`, `node resource`, `edge assign`, `edge request`, `cycle`, `deadlocked`, `instance used/free`. Böylece testler çizimi görmeden, sınıfları sayarak doğrulanabiliyor (örn. klasik deadlock'ta 2 `edge request cycle` olmalı).

### 5) Adım adım gezinme
Python bütün adımları sayfaya yazmaya devam ediyor; küçük bir JavaScript (`update()`) yalnızca o anki adımı görünür bırakıyor.
- **◀ Önceki / Sonraki ▶** düğmeleri ve klavyede **← / →**
- **Tümünü göster**: alt alta görünüm (rapora ekran görüntüsü için)
- JavaScript kapalıysa sayfa eskisi gibi bütün adımları gösterir, hiçbir şey kaybolmaz.

```bash
python3 -m src.run_scenario scenarios/hafta4_deadlock.json
python3 -m src.run_scenario scenarios/hafta4_dongu_deadlock_yok.json
open simulation_view.html
```

### 6) Testler
41 test, hepsi geçiyor (32 önceki + 9 yeni):
- `tests/test_week5_graph_view.py` (8): düğüm/kenar sayıları, örnek noktaları, döngü vurgusu, döngü dışı kenar, boş sistem, renk kuralı
- `tests/test_week5_stepper.py` (1): sayfada bütün adımlar ve gezinme kontrolleri var

← [[00-Genel/11 Haftalık Plan]]
