---
tags: [deadlock-guardian, plan]
---
# 11 Haftalık Geliştirme Planı

> Hocaya teslim edilen sürüm: ![[04-Kaynaklar/Deadlock_Guardian_11_Haftalik_Plan.pdf]]
> PDF'i yeniden üretmek için: `04-Kaynaklar/plan_pdf_uret.py`

| Hafta | Aşama | Yapılacak çalışmalar | Haftanın çıktısı | Durum |
|---|---|---|---|---|
| 1 | Konuyu Anlama ve Tasarım | Kavramlar, kapsam, modüller, teknoloji, görev dağılımı, GitHub deposu | Proje tanım belgesi, kod deposu | ✅ |
| 2 | [[01-Notlar/Haftalar/Hafta 02 - Basit Simülasyon\|Basit Simülasyon]] | Process/Resource yapıları; isteme, bırakma, WAITING; bırakılan kaynağın bekleyene verilmesi | Konsolda çalışan temel simülasyon | ⏳ |
| 3 | [[01-Notlar/Haftalar/Hafta 03 - Kaynak İlişkileri\|Kaynak İlişkileri]] | Allocation/request tabloları, çok örnekli kaynaklar, olay kaydı, senaryoların dosyadan yüklenmesi | Senaryo dosyasıyla çalışan sistem, durum tablosu | ✅ |
| 4 | [[01-Notlar/Haftalar/Hafta 04 - Deadlock Tespiti\|Deadlock Tespiti]] | RAG + DFS ile döngü arama, çok örnekli kaynaklar için detection algoritması, raporlama | Tespit modülü ve birim testleri | ✅ |
| 5 | [[01-Notlar/Haftalar/Hafta 05 - Görselleştirme\|Görselleştirme]] | Graf çizimi, tutma/bekleme kenarları, döngünün vurgulanması | RAG ekranı | ✅ |
| 6 | Risk Analizi | Banker's Algorithm ile güvenli durum kontrolü, istek öncesi uyarı | Güvenli/güvensiz durum uyarıları | |
| 7 | Risk Seviyesi Sistemi | Low/Medium/High/Critical seviyeleri ve nedenleri | Risk göstergesi ve açıklamalar | |
| 8 | Recovery | Process sonlandırma, kaynak geri alma, en düşük maliyetli kurbanın seçilmesi, SAFE'e dönüş | Çalışan kurtarma modülü | |
| 9 | Kullanıcı Arayüzü | Tüm modüllerin tek dashboard'da birleştirilmesi | Bütünleşik arayüz | |
| 10 | Test ve İyileştirme | Normal, tek/çoklu deadlock ve recovery senaryolarının testi, hata düzeltme | Test raporu, kararlı sürüm | |
| 11 | Final Hazırlığı | Son kontroller, demo senaryosu, rapor, sunum | Final demo, rapor ve sunum | |

**11. haftanın sonunda:** process/resource simüle eden, ilişkileri takip eden, riski gösteren, deadlock'u tespit eden ve recovery sunan çalışan bir prototip.

← [[00-Genel/Proje Ana Sayfa]]
