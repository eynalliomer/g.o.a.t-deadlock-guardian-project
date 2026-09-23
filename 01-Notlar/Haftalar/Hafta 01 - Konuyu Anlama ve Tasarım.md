---
tags: [deadlock-guardian, hafta]
hafta: 1
durum: tamamlandi
---
# Hafta 1: Konuyu Anlama ve Proje Tasarımı

**Amaç:** Deadlock konusunu kavramak ve projenin sınırlarını netleştirmek.

## Yapılanlar
- [x] Proje fikri seçildi: fikir havuzundan Deadlock Guardian'a geçiş → [[00-Genel/Karar Geçmişi]]
- [x] Proje tanımı yazıldı → [[00-Genel/Proje Tanımı]]
- [x] 11 haftalık plan hazırlandı ve hocaya teslim edilecek PDF'e dönüştürüldü → [[00-Genel/11 Haftalık Plan]]
- [x] 11 haftanın kavramlarını anlatan el kitabı hazırlandı → `04-Kaynaklar/Deadlock_Guardian_El_Kitabi.pdf`
- [x] Teknoloji seçildi: Python, Git + GitHub, VS Code, macOS
- [x] Git deposu kuruldu ve GitHub'a yüklendi
- [x] Klasör yapısı oluşturuldu: `src/`, `scenarios/`, `tests/`

## Öğrenilen kavramlar (El kitabı Bölüm 1)
- İşletim sistemi = kaynak dağıtıcı
- Program ve process farkı, process durumları, PCB
- Kaynak tipi ve örnek (instance); request → use → release döngüsü
- Deadlock tanımı ve dört Coffman koşulu: mutual exclusion, hold and wait, no preemption, circular wait
- Deadlock, starvation ve livelock farkı
- Dört başa çıkma yöntemi: prevention, avoidance, detection + recovery, ignore

## Alınan kararlar
- İlk sürüm kontrollü bir **simülasyon**, gerçek process'ler yönetilmiyor.
- Proje **tek kişi** (Ömer) tarafından, Claude ile birlikte VS Code'da geliştiriliyor. Hocaya teslim edilen planda 4 kişilik rol dağılımı yer alıyor.
- Her haftanın sonu GitHub'da `hafta-XX` etiketiyle işaretleniyor.

## Açık kalanlar
- [ ] Arayüz teknolojisi: PyQt mı, web mi? (5. haftadan önce)
- [ ] Veri: JSON mu, SQLite mı? (3. haftada; şimdilik JSON)

**Haftanın çıktısı:** proje tanım belgesi ve kurulmuş kod deposu.

→ Sonraki: [[01-Notlar/Haftalar/Hafta 02 - Basit Simülasyon]]
