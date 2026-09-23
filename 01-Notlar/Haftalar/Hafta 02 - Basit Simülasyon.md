---
tags: [deadlock-guardian, hafta]
hafta: 2
durum: devam
---
# Hafta 2: Basit Simülasyon

**Amaç:** Process ve Resource yapılarını oluşturmak ve temel kaynak işlemlerini çalıştırmak.

## Yapılacaklar
- [ ] Process oluşturma (P1, P2, P3…)
- [ ] Resource oluşturma (R1, R2, R3…)
- [ ] Kaynak alma: process boş bir kaynağı alabilmeli
- [ ] Kaynak bırakma: process tuttuğu kaynağı serbest bırakabilmeli
- [ ] Bekleme: kaynak doluysa isteyen process `WAITING` durumuna geçmeli

## Örnek akış
```
P1 → R1 aldı
P2 → R1 istedi → R1 dolu → P2 WAITING
P1 → R1 bıraktı → R1 P2'ye verildi
```

## Hafta sonu hedefi
Process ve resource oluşturabilen, kaynak verip bırakabilen ve kaynak doluyken process'i bekletebilen çalışan bir simülasyon.

> [!note] Bu hafta kapsam dışı
> Deadlock tespiti, risk analizi ve recovery yok. Amaç, sonraki haftaların üzerine kurulacağı temel altyapıyı oluşturmak.

← [[00-Genel/11 Haftalık Plan]]
