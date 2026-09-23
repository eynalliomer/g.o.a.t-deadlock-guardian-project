# Deadlock Guardian

> Process'lerin kaynak kullanımını izleyen, deadlock riskini değerlendiren, oluşan deadlock'u tespit eden ve sistemi yeniden güvenli hale getirmek için recovery seçenekleri sunan bir işletim sistemi simülasyon projesi.

**Ders:** İşletim Sistemleri · Yazılım Mühendisliği
**Süre:** 11 hafta
**Ana kaynak:** Silberschatz, Galvin, Gagne — *Operating System Concepts*, 10. baskı, Bölüm 8 (Deadlocks)

## Proje ne yapıyor?

Deadlock, birden fazla process'in birbirinin tuttuğu kaynağı beklemesi yüzünden hiçbirinin ilerleyememesi durumudur. Deadlock Guardian bu durumu kontrollü bir simülasyonda canlandırır ve üç iş yapar:

1. **Risk analizi:** deadlock oluşmadan önce tehlikeli durumu fark eder (Banker's Algorithm, risk seviyeleri).
2. **Tespit:** oluşan deadlock'u bulur (Resource Allocation Graph, döngü arama, detection algoritması).
3. **Recovery:** kurban process'i seçip sistemi tekrar güvenli duruma getirir.

## Haftalık ilerleme

| Hafta | Aşama | Durum |
|---|---|---|
| 1 | Konuyu anlama ve proje tasarımı | ✅ Tamamlandı |
| 2 | Basit simülasyon | ⏳ Sırada |
| 3 | Kaynak ilişkileri | |
| 4 | Deadlock tespiti | |
| 5 | Görselleştirme | |
| 6 | Risk analizi (Banker's Algorithm) | |
| 7 | Risk seviyesi sistemi | |
| 8 | Recovery | |
| 9 | Kullanıcı arayüzü | |
| 10 | Test ve iyileştirme | |
| 11 | Final: demo, rapor, sunum | |

Her haftanın sonu Git'te `hafta-01`, `hafta-02`… etiketleriyle işaretlenir.

## Klasör yapısı

```
├── 00-Genel/        Proje tanımı, 11 haftalık plan, kararlar
├── 01-Notlar/       Haftalık çalışma notları
├── 02-Tasarim/      Tasarım kararları
├── 03-Gunluk/       Günlük ilerleme kayıtları
├── 04-Kaynaklar/    PDF'ler (plan, el kitabı) ve bunları üreten betikler
├── src/             Kaynak kod
├── scenarios/       JSON senaryo dosyaları
└── tests/           pytest testleri
```

Notlar [Obsidian](https://obsidian.md) ile yazılır; klasör aynı zamanda bir Obsidian kasasıdır. GitHub'da da normal Markdown olarak okunabilir.

## Belgeler

- [Proje tanımı](00-Genel/Proje%20Tanımı.md)
- [11 haftalık plan](00-Genel/11%20Haftalık%20Plan.md) · [PDF](04-Kaynaklar/Deadlock_Guardian_11_Haftalik_Plan.pdf)
- [El kitabı: 11 haftanın bilgi havuzu](04-Kaynaklar/Deadlock_Guardian_El_Kitabi.pdf)

## Çalıştırma

Kod 2. haftadan itibaren eklenecek. Kurulum:

```bash
python3 -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```
