---
tags: [deadlock-guardian, hafta]
hafta: 10
durum: tamamlandı
---
# Hafta 10: Test ve İyileştirme

**Amaç:** Normal, tek/çoklu deadlock ve recovery senaryolarının testi, hata düzeltme.

## Yapılacaklar
- [x] Uç durumların (edge cases) denenmesi, bulunan hataların düzeltilmesi
- [x] El kitabındaki 5 sistem testi senaryosu
- [x] Çoklu deadlock'ta bütün döngülerin raporlanması
- [x] Kod kapsamı ölçümü ve eksik testlerin tamamlanması
- [x] Test raporu → [[02-Tasarim/Test Raporu]]

## Hafta sonu hedefi
Test raporu, kararlı sürüm.

## Uygulama notları

### 1) Uç durumlar: 5 hata bulundu
Testlerden önce şüpheli durumlar elle denendi. Her hata için önce onu yakalayan test yazıldı (kırmızı), sonra düzeltildi (yeşil):

| Durum | Hata | Düzeltme |
|---|---|---|
| Toplamdan fazla istek | Process sonsuza kadar bekliyor, tespit algoritması görmüyordu | `Resource.acquire` reddediyor |
| Negatif miktar | Kaynak "üretiliyordu" (toplam 1, boşta 4) | Miktar en az 1 olmalı |
| Sıfır miktar | Tabloda boş `P1: 0` kaydı | Miktar en az 1 olmalı |
| Beklemedeki process eylem yapıyor | İki kuyrukta birden, durumu yanlışlıkla READY | Motor reddediyor: bekleyen process bloke durumdadır |
| Senaryoda olmayan kaynak | `AttributeError`, web sayfası çöküyordu | Motor anlaşılır `ValueError` veriyor |

**Bilinçli davranış:** Kendi tuttuğu kaynağı tekrar isteyen process kendini kilitliyor ve tespit algoritması bunu yakalıyor. Tekrar girilemeyen (non-reentrant) kilitlerde gerçek sistemler de böyle davranır. Toplamdan fazla istekten farkı: o hiç görünmeyen bir sonsuz bekleme yaratıyordu.

**İlke:** Doğrulama, durumu değiştirmeden **önce** yapılıyor; hatalı eylem sistemi yarım bırakmıyor.

### 2) Sistem testleri ve çoklu deadlock
El kitabının 5 senaryosu `tests/test_week10_system.py`'de. İkisi için yeni senaryo yazıldı: `hafta10_normal_calisma.json`, `hafta10_coklu_deadlock.json`.

Çoklu deadlock senaryosu gerçek bir eksiği ortaya çıkardı: `find_cycle` ilk döngüde duruyordu, iki bağımsız deadlock olduğunda raporda yalnızca biri görünüyordu. **`find_cycles()`** eklendi: bir döngü bulununca onun düğümlerini graftan çıkarıp aramayı tekrarlıyor. Rapor ("Döngü 1: … | Döngü 2: …"), risk nedenleri ve graf vurgusu artık bütün ayrık döngüleri gösteriyor. Recovery iki döngüyü iki ayrı kurtarmayla çözüyor.

### 3) Kod kapsamı
`pytest-cov` ile ölçüldü:
1. İlk ölçüm **%90**: komut satırı araçları test edilmemişti → duman testleri.
2. Kalan satırlar incelendi: hepsi `__main__` satırı değildi. **Web arayüzünün iki güvenlik doğrulaması** ve iki görünüm dalı hiç çalıştırılmamıştı → 5 test.
3. Son durum **%99**: kalan 4 satır `__main__` satırları ve bir `__repr__`.

Ders: Kapsam yüzdesi tek başına yetmez; kalan satırların **ne olduğuna** bakmak gerekir.

### 4) Port değişikliği: 5000 → 5050
Web sunucusu yeniden başlatılırken macOS'in AirPlay alıcısının (`ControlCenter`) da 5000 portunu dinlediği görüldü. Bizim sunucu yalnızca `127.0.0.1`'e bağlandığı için bu makinede çakışmıyordu, ama `localhost:5000` yazılırsa ya da demo başka bir Mac'te yapılırsa sorun çıkabilirdi. Varsayılan port **5050** yapıldı.

```bash
python -m src.app          # http://127.0.0.1:5050
python -m pytest --cov=src # testler + kod kapsamı
```

### 5) Sonuç
127 test, hepsi geçiyor; kod kapsamı %99; 5 sistem senaryosu beklenen sonucu veriyor. Ayrıntılar: [[02-Tasarim/Test Raporu]].

← [[00-Genel/11 Haftalık Plan]]
