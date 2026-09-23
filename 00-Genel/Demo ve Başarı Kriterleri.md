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

## Başarı kriterleri
- [ ] En az bir deadlock senaryosunu doğru tespit etmek
- [ ] Deadlock'a dahil process ve kaynakları göstermek
- [ ] Belirlenen koşullarda deadlock risk uyarısı vermek
- [ ] En az bir recovery yöntemi uygulamak
- [ ] Recovery sonrası sistemin güvenli duruma döndüğünü göstermek
- [ ] Normal ve deadlock durumlarını karşılaştırmak
- [ ] Kodun modüler olması (üyeler ayrı çalışabilmeli)
- [ ] Finalde baştan sona çalışan bir demo

← [[00-Genel/Proje Ana Sayfa]]
