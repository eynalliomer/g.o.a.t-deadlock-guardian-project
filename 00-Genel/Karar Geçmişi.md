---
tags: [deadlock-guardian, karar]
---
# Karar Geçmişi

## 1. Filtre: özgün ve yazılımla geliştirilebilir olmalı
Hedef "bir OS algoritmasını kodlamak" değil, OS bilgisini motor olarak kullanan gerçek bir **yazılım ürünü** geliştirmekti.
- **Zayıf proje:** "Round Robin implement edildi, Gantt chart çizildi."
- **Güçlü proje:** OS mekanizmasını analiz eden, izleyen ve yöneten bir sistem yazılımı.

İnternette CPU scheduler, page replacement ve shell simülatörleri zaten çok yaygın olduğu için bunların sade halleri elendi.

## 2. Önerilen fikir havuzu (ilk tur)
TaskPilot, FocusOS, SafeRun, CrashVault, ProcessLens, RAMGuard, LocalOS, RescueFS, ThreadFlow, **DeadlockGuard**, SmartCache, OSWatch, MiniCloud, FileTime Machine, DevSandbox.

## 3. Tahtadaki konuların özgünleştirilmiş hali (ikinci tur)
| Temel konu | Özgün proje |
|---|---|
| CPU zamanlama | Adaptive CPU Scheduler |
| Komut satırı | SmartOS Shell |
| Dosya yönetim sistemi | Versioned Intelligent FS |
| Kernel module | Kernel Activity Monitor |
| Görev yöneticisi | Process Intelligence Manager |
| Container / Sandbox | Mini Container Platform |
| Çoklu işlemci / senkronizasyon | Parallel Job Orchestrator |
| Sayfa değiştirme | Adaptive Memory Manager |
| **Deadlock** | **Deadlock Detective** |
| Veritabanlı OS | Persistent OS State Manager |
| Multi-thread | Concurrent Processing Engine |

## 4. Nihai karar: Deadlock Guardian
Ekip **deadlock** konusunu seçti. Önceki deadlock fikirlerinin üç temel özelliği tek bir sistemde birleştirildi: **Risk Analizi + Deadlock Detection + Recovery**. Ayrıntılar: [[00-Genel/Proje Tanımı]].

## Üretilen teslim belgeleri
- 2. hafta "Basit Simülasyon" özeti (PDF, önceki sohbette üretildi)
- 11 haftalık plan PDF'i ve konuşma özeti `.md` dosyası önceki sohbette hata yüzünden **üretilemedi**. İçerikleri bu kasadaki notlara aktarıldı.

← [[00-Genel/Proje Ana Sayfa]]
