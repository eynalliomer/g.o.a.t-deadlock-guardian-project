---
tags: [deadlock-guardian, demo]
---
# Demo ve Başarı Kriterleri

## Final demo senaryosu
1. Sistemi açıyoruz.
2. Üç process ve üç kaynak oluşturuyoruz.
3. Kaynakları process'lere dağıtıyoruz.
4. İki process'in birbirini beklediği senaryoyu oluşturuyoruz.
5. Sistem risk artışını gösteriyor.
6. Deadlock oluşuyor.
7. Sistem hangi process ve kaynakların probleme neden olduğunu gösteriyor.
8. Recovery seçenekleri çıkıyor.
9. Bir process'i sonlandırıyoruz ve kaynakları serbest bırakıyoruz.
10. Sistem tekrar **SAFE** durumuna geçiyor.

Kısa akış: `Normal sistem → kaynak talepleri → risk artışı → deadlock → tespit → recovery → güvenli durum`

Uygulaması: `scenarios/final_demo.json` → [[01-Notlar/Haftalar/Hafta 11 - Final Hazırlığı]]

## Başarı kriterleri
- [x] En az bir deadlock senaryosunu doğru tespit etmek (tek, çoklu ve çok örnekli kaynaklı senaryolar)
- [x] Deadlock'a dahil process ve kaynakları göstermek (durum paneli, kart vurgusu, graf üzerinde döngü)
- [x] Belirlenen koşullarda deadlock risk uyarısı vermek (4 risk seviyesi + Banker's uyarısı)
- [x] En az bir recovery yöntemi uygulamak (sonlandırma ve kaynak geri alma)
- [x] Recovery sonrası sistemin güvenli duruma döndüğünü göstermek (Banker's güvenli sıra buluyor)
- [x] Normal ve deadlock durumlarını karşılaştırmak (`hafta10_normal_calisma.json` ve risk seyri)
- [x] Kodun modüler olması (katmanlı mimari; algoritmalar arayüzden bağımsız test edildi)
- [x] Finalde baştan sona çalışan bir demo (`scenarios/final_demo.json`, `python -m src.app`)

← [[00-Genel/Proje Ana Sayfa]]
