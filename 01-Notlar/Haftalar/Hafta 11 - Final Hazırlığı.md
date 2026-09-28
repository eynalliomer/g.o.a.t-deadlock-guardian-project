---
tags: [deadlock-guardian, hafta]
hafta: 11
durum: tamamlandı
---
# Hafta 11: Final Hazırlığı

**Amaç:** Son kontroller, demo senaryosu, rapor, sunum.

## Yapılacaklar
- [x] Final demo senaryosu (`scenarios/final_demo.json`)
- [x] Türkçe ek düzeltmesi (R3'ten, R6'dan): demoda görünen metinler
- [x] Proje raporu (PDF) → `04-Kaynaklar/Deadlock_Guardian_Final_Rapor.pdf`
- [x] Sunum (tarayıcıda slayt) → https://claude.ai/artifact/4SJH2ECynnxoMgHvsXrAG4
- [x] Başarı kriterlerinin kontrolü → [[00-Genel/Demo ve Başarı Kriterleri]]

## Demo öncesi yapılacaklar (el kitabı 11.1)
- [ ] Raporda kapaktaki "Hazırlayanlar" ve 9. bölümdeki "Sorumlu" sütununu doldur, PDF'i yeniden üret
- [ ] Sunumdaki `[__]` (Hazırlayanlar) yer tutucusunu doldur
- [ ] Sunumu Paylaş menüsünden hoca/sınıfla paylaş (şu an yalnızca sen açabiliyorsun)
- [ ] Demoyu en az iki kez prova et, bir kez de başka bir bilgisayarda
- [ ] Yedek olarak demonun ekran kaydını al
- [ ] Sınıftaki bilgisayarda: `pip install -r requirements.txt`, `python -m src.app`, tarayıcıda http://127.0.0.1:5050

## Uygulama notları

### 1) Final demo senaryosu
El kitabındaki demo akışını birebir izleyen, **JSON dosyası olarak hazırlanmış** bir senaryo (el kitabı: "elle tıklamaya güvenmeyin"). 3 process, 3 kaynak (R3'ün 2 birimi var):

| Adım | Olay | Risk | Banker's |
|---|---|---|---|
| 0–2 | Başlangıç; P1, R1 ve R3'ten birer birim alıyor | LOW | SAFE |
| 3 | P3, R3'ten 2 birim istiyor (1 boş) → bekler | MEDIUM | WAIT |
| 4 | P2, R2'yi alıyor | **HIGH** | **UNSAFE** |
| 5 | P1, R2'yi istiyor → bekler | HIGH | WAIT |
| 6 | P2, R1'i istiyor → P1 ile P2 birbirini bekliyor | **CRITICAL** | WAIT |
| 7 | Recovery: **Sonlandır: P1** (maliyet 6, önerilen) | MEDIUM | Güvenli: P2 → P3 |
| 8–10 | P2 ve P3 işini bitiriyor | LOW | Güvenli |

Senaryo, her adımın hedeflenen risk seviyesini üretip üretmediği motorla doğrulanarak tasarlandı. P1 hem R1'i hem R3'ü tuttuğu için onu sonlandırmak 2 birim serbest bırakıyor; bu yüzden en ucuz seçenek o, bu da demo akışındaki "önerilen kurbanı sonlandırıyoruz" adımıyla uyuşuyor.

### 2) Türkçe ek düzeltmesi
Demo senaryosunda R3 kullanılınca "R3'**den**" hatası göründü; doğrusu "R3'**ten**" (üç → üç**ten**). Önceki senaryolar yalnızca R1/R2 kullandığı için ("bir**den**", "iki**den**") fark edilmemişti. `src/turkish.py`'deki `ablative()` eki, adın son rakamının okunuşuna göre (sert ünsüz → t, kalın ünlü → a) seçiyor; harfle biten adlar için ünlü uyumu. Başlıklarda ve hata mesajlarında kullanılıyor. **Sınırlama:** yalnızca son rakama bakılıyor; R20 gibi onluklarda ek yanlış olabilir.

### 3) Proje raporu (PDF, 17 sayfa)
El kitabı 11.2'deki 9 bölüm: özet, giriş, teorik arka plan, tasarım (mimari şeması dahil), gerçekleştirme (önemli kod parçaları), test ve sonuçlar (demo ekran görüntüleriyle), sonuç ve gelecek çalışmalar, kaynakça, ekip katkıları (Sorumlu sütunu boş, doldurulacak).

```bash
python 04-Kaynaklar/ekran_goruntusu_al.py   # dashboard görüntüleri (kod değiştiyse)
python 04-Kaynaklar/final_rapor_uret.py     # raporu yeniden üretir
```
`ekran_goruntusu_al.py` sunucu gerektirmiyor: motoru istenen adıma kadar oynatıp dashboard HTML'ini Chrome'un başsız moduyla PNG'ye çeviriyor.

### 4) Sunum (15 slayt)
El kitabı 11.3: "Teoriyi az, demoyu çok tutun." Bölümler: problem (3), çözüm (6), demo (canlı demoya geçiş + 2 yedek ekran görüntüsü), sonuç (test sonuçları, sonuç, sorular). Her slaytta konuşmacı notu var; son slayt el kitabındaki olası üç soruyu kısa cevaplarıyla içeriyor.

← [[00-Genel/11 Haftalık Plan]]
