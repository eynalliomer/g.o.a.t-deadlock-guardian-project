---
tags: [deadlock-guardian, hafta]
hafta: 2
durum: tamamlandı
---
# Hafta 2: Basit Simülasyon

**Amaç:** Process ve Resource yapılarını oluşturmak ve temel kaynak işlemlerini çalıştırmak.

## Yapılacaklar
- [x] Process oluşturma (P1, P2, P3…)
- [x] Resource oluşturma (R1, R2, R3…)
- [x] Kaynak alma: process boş bir kaynağı alabilmeli
- [x] Kaynak bırakma: process tuttuğu kaynağı serbest bırakabilmeli
- [x] Bekleme: kaynak doluysa isteyen process `WAITING` durumuna geçmeli

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

## Uygulama notları

### 1) Python sanal ortamı (venv) neden ve nasıl kuruldu
**Neden:** Bilgisayardaki Python kurulumu tüm projeler arasında paylaşılır. Bir projeye özel paket (örn. `pytest`) kurunca bu, sistem genelini etkilememeli; ayrıca ekip arkadaşlarının aynı proje için aynı bağımlılık sürümlerini kullanması gerekir. Sanal ortam (virtual environment), projeye özel, izole bir Python kopyası + paket klasörü oluşturur.

**Nasıl:**
```bash
python3 -m venv .venv          # .venv klasöründe izole ortam oluşturur
source .venv/bin/activate      # ortamı aktif eder (terminalde (.venv) görünür)
pip install pytest             # paket sadece bu ortama kurulur
```
`.venv/` klasörü `.gitignore`'da zaten hariç tutuluyordu, yani GitHub'a **gönderilmiyor** — her geliştirici kendi makinesinde `python3 -m venv .venv` ile kendi kopyasını kurar. Bağımlılıkların listesi `requirements.txt` dosyasında tutulur ki başkası `pip install -r requirements.txt` ile aynı paketleri kurabilsin.

### 2) `src/process.py` — Process sınıfı
Bir **process**, kaynak isteyen/kullanan/bırakan aktördür (Silberschatz böl. 8). İki parça yazıldı:

```python
class ProcessState(Enum):
    READY = auto()
    WAITING = auto()
```
`Enum` kullanmamızın sebebi: process durumunu düz bir string ("ready", "Ready", "READY"...) olarak tutsaydık yazım hatası riski olurdu ve IDE bunu yakalayamazdı. `Enum` ile sadece tanımlı iki değerden biri kullanılabilir, hata derleme/çalışma zamanında hemen belli olur.

```python
class Process:
    def __init__(self, name: str):
        self.name = name
        self.state = ProcessState.READY
        self.held_resources = []
```
Yeni bir process oluşturulduğunda varsayılan olarak **READY** (bekleyen bir şey yok) olur ve elinde hiçbir kaynak tutmaz (`held_resources = []`). `__repr__` metodu sadece hata ayıklamayı (debug) kolaylaştırmak için var: `print(p1)` dediğimizde bellek adresi yerine okunabilir bir özet (`Process(P1, state=READY, held=[])`) görürüz.

### 3) `src/resource.py` — Resource sınıfı
Bir **kaynak**, sınırlı sayıda örneği olan paylaşılan bir şeydir (yazıcı, bellek bloğu vb.). Bu hafta kapsamı gereği **tek örnekli** kaynaklarla başladık (çok örnekli kaynaklar hafta 3'e ait).

```python
class Resource:
    def __init__(self, name: str):
        self.name = name
        self.owner = None          # kimse tutmuyorsa None
        self.waiting_queue = []    # kaynağı bekleyen process'ler, FIFO sırayla
```

`acquire(process)` — bir process kaynağı **istediğinde** çağrılır:
- Kaynak boşsa (`owner is None`): hemen o process'e verilir, process `READY` kalır, kaynağın adı `held_resources`'a eklenir, `True` döner.
- Kaynak doluysa: isteyen process **WAITING** durumuna geçer ve `waiting_queue`'ya eklenir (aynı process iki kez kuyruğa girmesin diye kontrol edilir), `False` döner.

`release(process)` — bir process elindeki kaynağı **bıraktığında** çağrılır:
- Önce güvenlik kontrolü: kaynağın gerçek sahibi olmayan biri onu bırakamaz (aksi halde mantıksız/hatalı bir simülasyon durumu oluşurdu) → `ValueError` fırlatılır.
- Kaynak gerçekten boşaltılır (`owner = None`), process'in `held_resources` listesinden çıkarılır.
- **En önemli kısım:** kuyrukta bekleyen process varsa, kaynağı otomatik olarak sıradaki process'e (`waiting_queue.pop(0)` → FIFO, ilk gelen ilk alır) verir. Bunu elle (`self.owner = next_process` gibi) tekrar yazmak yerine, **`self.acquire(next_process)` çağırarak** yapıyoruz.

**Neden `acquire()`'ı tekrar çağırdık, elle atamadık?** Bu, yazılım mühendisliğinde **DRY (Don't Repeat Yourself)** prensibi. `acquire()` zaten "kaynağı ver + process'i READY yap + held_resources'a ekle" işinin **tek doğru kaynağı**. Bu üç satırı `release()` içinde tekrar yazsaydık, ileride bu mantığı değiştirmemiz gerektiğinde (örn. loglama eklemek) iki yeri de güncellememiz gerekirdi — biri unutulursa gizli bir hata (bug) doğardı. Tek yerden yönetmek kodu hem kısaltır hem de tutarlılığı garantiler.

### 4) `src/simulation.py` — konsol demosu
Hafta 2'nin "çıktısı" olan, iki sınıfı bir araya getirip senaryoyu gözle görülür şekilde çalıştıran küçük bir script:
```
P1 → R1 aldı
P2 → R1 istedi → R1 dolu → P2 WAITING
P1 → R1 bıraktı → R1 otomatik P2'ye verildi
```
Çalıştırma: `python -m src.simulation` (proje kök dizininden, sanal ortam aktifken).

### 5) `tests/test_week2_simulation.py` — birim testler
5 test yazıldı ve `pytest` ile doğrulandı (`python -m pytest tests/ -v`):
1. Yeni process READY ve boş kaynak listesiyle başlıyor mu?
2. Boş kaynak doğrudan veriliyor mu?
3. Meşgul kaynağı isteyen process WAITING oluyor mu ve kuyruğa giriyor mu?
4. `release()` kaynağı bekleyen process'e doğru devrediyor mu (state, held_resources, kuyruk boşalması)?
5. Sahibi olmayan bir process kaynağı bırakmaya çalışırsa `ValueError` fırlıyor mu?

**Neden testler önemli:** İlerleyen haftalarda (detection, recovery, Banker's algoritması) bu `Process`/`Resource` sınıflarının üzerine inşa edeceğiz. Eğer birisi ileride bu dosyaları değiştirirse, testler bozulan bir şey olup olmadığını anında gösterir — sunumda "bu çalışıyor" demek yerine kanıtımız olur.

### 6) `src/__init__.py`
Boş bir dosya. Python'a `src` klasörünün bir **paket** olduğunu bildirir, böylece `from src.process import Process` gibi importlar çalışır.

← [[00-Genel/11 Haftalık Plan]]
