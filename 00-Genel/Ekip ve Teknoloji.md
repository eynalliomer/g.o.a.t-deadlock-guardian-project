---
tags: [deadlock-guardian, ekip]
---
# Ekip ve Teknoloji

## Görev dağılımı (4 kişilik ekip)
| Üye | Ana sorumluluk | Örnek görevler | İlgili haftalar |
|---|---|---|---|
| Üye 1 | Simülasyon ve veri modeli | Process/Resource yapıları, simülasyon motoru, senaryo dosyaları, test senaryoları | 2, 3, 10 |
| Üye 2 | Deadlock tespiti ve recovery | RAG, DFS ile döngü arama, detection algoritması, kurban seçimi, kurtarma | 4, 8 |
| Üye 3 | Risk analizi | Banker's Algorithm, safe state, risk puanlama, Low/Medium/High/Critical | 6, 7 |
| Üye 4 | Arayüz ve görselleştirme | Dashboard, graf çizimi, kullanıcı akışı, sonuç ekranları | 5, 9 |

> Üye isimleri henüz belirlenmedi. Rolleri kimin alacağı netleşince buraya yazılacak.

## Teknoloji
| Katman | Öneri | Neden |
|---|---|---|
| Simülasyon | Python | Hızlı geliştirme, kolay test |
| Algoritmalar | Python | Graf ve veri yapıları rahat uygulanır |
| Arayüz | PyQt **veya** basit web arayüzü | Dashboard ve grafik göstermek için (karar verilmedi) |
| Veri | JSON / SQLite | Senaryoları ve sonuçları saklamak için (karar verilmedi) |
| Ekip çalışması | Git + GitHub | Kod paylaşımı, branch, sürüm takibi |

**İlke:** Kod, ekip üyelerinin birbirinden bağımsız çalışabileceği şekilde modüler olmalı.

← [[00-Genel/Proje Ana Sayfa]]
