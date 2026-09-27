---
tags: [deadlock-guardian, hafta]
hafta: 9
durum: tamamlandı
---
# Hafta 9: Kullanıcı Arayüzü

**Amaç:** Tüm modüllerin tek dashboard'da birleştirilmesi.

## Yapılacaklar
- [x] Arayüz teknolojisi kararı (PyQt mı, web mi?)
- [x] Simülasyon motorunun ekrandan ayrılması (`Simulation`)
- [x] Web dashboard: özet kartları, durum, RAG, process/kaynak kartları, olay akışı
- [x] Senaryo yükle, adım adım ilerlet, geri al, sıfırla
- [x] Kurtarma seçeneğini düğmeyle canlı uygulama; senaryo dışı elle eylem
- [x] Risk / deadlock / Banker's şeritlerinin tek "Durum" panelinde birleştirilmesi
- [x] Testler

## Hafta sonu hedefi
Bütünleşik arayüz.

## Uygulama notları

### 1) Karar: web (Flask + tarayıcı) (2026-09-28)
| | PyQt | Web (Flask) | Statik HTML |
|---|---|---|---|
| Mevcut görsel kod | Yeniden yazılır (QGraphicsView) | **Tamamen yeniden kullanılır** | Yeniden kullanılır |
| Canlı etkileşim | Var | **Var** | Yok |
| Demo | Uygulamayı aç | `python -m src.app` + tarayıcı | Dosyayı aç |

Hafta 2'den beri bütün görsel kod (kartlar, SVG graf, risk seyri) HTML ürettiği için web seçildi: hiçbir şey çöpe gitmedi ve düğmeler Python'u canlı çağırabiliyor.

### 2) Mimari: MVC ve sorumlulukların ayrılması
| Katman | Dosya | Görevi |
|---|---|---|
| **Model** | `src/engine.py` | `Simulation`: durumu tutar, eylemleri uygular, analiz eder. Ekranı bilmez. |
| **View** | `src/dashboard_view.py` | Sayfayı çizer; kart ve graf kodunu statik önizlemeyle ortak kullanır. |
| **Controller** | `src/app.py` | Düğmelerden gelen istekleri motora iletir. |

**Refactor:** Olay uygulama mantığı önceden `run_scenario.py` ve `scenario_loader.py`'de iki ayrı kopya olarak duruyordu; artık yalnızca motorda. Konsol aracı, yükleyici ve web arayüzü aynı motoru kullanıyor. Önceki haftaların bütün testleri refactor'dan sonra değişmeden geçti.

### 3) Geri al: event sourcing
Motor her durumu **"başlangıç senaryosu + uygulanan eylemler listesi"** olarak tanımlıyor. "Geri al" = baştan başla, son eylem hariç hepsini yeniden oynat. Simülasyon deterministik olduğu için her seferinde aynı duruma ulaşılıyor. Bir sonlandırmayı (TERMINATED) geri almak bile ayrıca kod gerektirmedi.

Her eylem "senaryodan mı geldi, elle mi yapıldı" bilgisini taşıyor; böylece elle yapılan bir eylemi geri almak senaryodaki sırayı bozmuyor.

### 4) Olay güdümlü akış (el kitabı 9.2)
Kullanıcı düğmeye basar → tarayıcı POST isteği gönderir → controller motora eylemi uygular → motor durumu günceller → sayfaya yönlendirilir → view yeni durumu çizer.

**POST → yönlendir → GET kalıbı:** Her eylemden sonra sayfaya yönlendirildiği için tarayıcıda "yenile"ye basmak aynı eylemi ikinci kez uygulamıyor.

### 5) Dashboard
- **Üst çubuk:** senaryo seç/yükle; ⟲ Sıfırla, ◀ Geri al, Sonraki olay ▶; "Olay 4 / 10 · Sıradaki: …"
- **Risk seyri** ve **özet kartları** (aktif process, boş/toplam kaynak, deadlock, risk)
- **Durum paneli:** risk seviyesi ve nedenleri, Banker's sonucu, son isteğin güvensizlik uyarısı. Hafta 7'den beri üst üste binen üç şerit burada birleşti.
- **Kurtarma seçenekleri:** her seçeneğin yanında "Uygula" düğmesi, önerilen işaretli
- **Elle eylem:** process, kaynak, birim → İste / Bırak
- **RAG**, **process/kaynak kartları**, **olay akışı** (en yenisi üstte)

### 6) Güvenlik
- Sunucu yalnızca `127.0.0.1`'de dinliyor (bu bilgisayardan erişilebilir).
- Senaryo yükleme `scenarios/` klasöründeki dosyalarla sınırlı; `../README.md` gibi istekler reddediliyor.
- Elle eylemde process ve kaynak adları mevcut listelerden seçiliyor, doğrulanıyor.
- Hatalı eylem sayfayı çökertmiyor; durum bozulmadan kırmızı hata mesajı gösteriliyor.

```bash
pip install -r requirements.txt   # flask eklendi
python -m src.app                 # http://127.0.0.1:5050 (hafta 10'da 5000'den taşındı: macOS AirPlay çakışması)
```

### 7) Testler
99 test, hepsi geçiyor (80 önceki + 19 yeni):
- `tests/test_week9_engine.py` (11): adım, analiz, elle eylem, kurtarma seçeneği, geri al (senaryo/elle/sonlandırma), hatalı eylem
- `tests/test_week9_app.py` (8): Flask `test_client` ile düğmeler: sayfa, sonraki olay, kurtarma, geri al/sıfırla, elle eylem, hata mesajı, senaryo değiştirme, klasör dışı dosya engeli

← [[00-Genel/11 Haftalık Plan]]
