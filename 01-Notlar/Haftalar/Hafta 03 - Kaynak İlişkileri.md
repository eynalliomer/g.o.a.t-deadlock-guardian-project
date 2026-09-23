---
tags: [deadlock-guardian, hafta]
hafta: 3
durum: tamamlandı
---
# Hafta 3: Kaynak İlişkileri

**Amaç:** Allocation/request tabloları, çok örnekli kaynaklar, olay kaydı, senaryoların dosyadan yüklenmesi.

## Yapılacaklar
- [x] Çok örnekli kaynak desteği (bir kaynağın birden fazla birimi olabilmesi)
- [x] Allocation/request tabloları (kim, hangi kaynaktan, kaç birim tutuyor/istiyor)
- [x] Olay kaydı (event log): her acquire/release/waiting olayının zaman sırasıyla kaydı
- [x] Senaryoların JSON dosyasından yüklenmesi
- [x] Durum tablosu (process ve resource durumlarının tablo halinde gösterimi)

## Hafta sonu hedefi
Senaryo dosyasıyla çalışan sistem ve durum tablosu.

> [!note] Bu hafta kapsam dışı
> Deadlock tespiti (RAG + döngü arama) hafta 4'e ait, henüz yok.

## Uygulama notları

### 1) Neden Resource sınıfını değiştirmek zorunda kaldık?
Hafta 2'de `Resource` tek örnekliydi: `owner` tek bir process ya da `None`. Gerçek sistemlerde bir kaynağın (örn. "3 yazıcı") **birden fazla birimi** olabilir ve birden fazla process aynı kaynak türünden pay alabilir. Bu yüzden `owner` (tek process) yerine **allocation tablosu** kullandık:

```python
class Resource:
    def __init__(self, name, total_instances=1, event_log=None):
        self.total_instances = total_instances
        self.allocation = {}       # {process: tutulan_adet}
        self.waiting_queue = []    # [(process, istenen_adet), ...]
```

`Process.held_resources` de aynı sebeple listeden (`["R1"]`) sözlüğe (`{"R1": 2}`) çevrildi — artık "hangi kaynaktan kaç birim tutuyorum" bilgisini taşıyor. Bu bilgi ileride **hafta 6'daki Banker's algoritması** için doğrudan gerekecek (algoritma "her process ne kadar tutuyor, ne kadar isteyebilir" bilgisine dayanır).

**Önemli sonuç:** API değiştiği için hafta 2'nin testleri kırıldı (`r.owner` artık yok). Bu **kötü bir şey değil** — testlerin görevi tam da bu: bir değişikliğin nerede etki ettiğini anında göstermek. Testleri yeni API'ye göre güncelledik, hepsi tekrar geçti.

### 2) Tüm-ya-da-hiç kuralı
Bir process, bir kaynaktan istediği miktarın **tamamını** alamıyorsa (örn. 2 istiyor, 1 boşta), kaynak **hiç verilmez**, process tamamen bekler (WAITING). Kısmi paylaşım yok.

**Neden böyle seçtik:** Bu, gerçek işletim sistemlerinde ve özellikle **Banker's algoritmasında** (hafta 6, Silberschatz böl. 8) kullanılan standart varsayımdır — bir isteğin ya tamamen karşılanması ya da process'in tamamen beklemesi, güvenli durum (safe state) hesaplamalarını basitleştirir. Kısmi paylaşım seçseydik, hafta 6'da modelle çelişirdik.

```python
def acquire(self, process, amount=1):
    if amount > self.available_instances:
        process.state = ProcessState.WAITING
        self.waiting_queue.append((process, amount))
        return False
    # ... tamamı karşılanabiliyorsa ver
```

### 3) Bekleme kuyruğunun "atlayarak servis" mantığı
Hafta 2'de kuyruk basit FIFO'ydu: ilk bekleyen, kaynak boşalınca hemen alırdı. Çok örnekli kaynakta bu yetersiz kalır: kuyruktaki ilk process 3 birim istiyor olabilir ama sadece 1 birim boşalmış olabilir; oysa kuyrukta arkada duran başka bir process sadece 1 birim istiyor olabilir ve hemen karşılanabilir.

`_serve_waiting_queue()` bu yüzden **kuyruğun tamamını tarar**, karşılanabilen her isteği (sırayla, ama karşılanamayanı atlayarak) hemen verir:

```python
def _serve_waiting_queue(self):
    still_waiting = []
    for waiting_process, wanted_amount in self.waiting_queue:
        if wanted_amount <= self.available_instances:
            self.acquire(waiting_process, wanted_amount)
        else:
            still_waiting.append((waiting_process, wanted_amount))
    self.waiting_queue = still_waiting
```

**Bilinmesi gereken sınırlama:** Bu yaklaşım teorik olarak **starvation** (sonsuz bekleme) riskine açıktır — küçük istekler sürekli öne geçip büyük bir isteği hep atlayabilir. Ders kapsamında (hafta 3) bunu basit tuttuk; ileride istenirse "en uzun bekleyene öncelik" gibi bir kural eklenebilir, ama plan bunu istemiyor.

### 4) `release()` içinde neden yine `acquire()` çağrılıyor?
Hafta 2'de öğrendiğimiz **DRY prensibi** burada da geçerli: kaynağı sıradaki bekleyene verirken, "allocation'a ekle + process'i READY yap + held_resources'a ekle" mantığını tekrar yazmak yerine `self.acquire(waiting_process, wanted_amount)` çağırıyoruz. Tek doğru kaynak, tek bakım noktası.

### 5) `src/event_log.py` — Olay kaydı
Sistemin **anlık durumu** (kim ne tutuyor) ile **geçmişte ne olduğu** farklı şeylerdir. `EventLog`, her `acquire`/`release`/`WAITING` olayını sırayla bir listeye kaydeden basit bir sınıf:

```python
class EventLog:
    def __init__(self):
        self.events = []

    def log(self, event_type, process_name, resource_name, amount, detail=""):
        self.events.append({...})
```

**Neden ayrı bir sınıf, neden Resource'un kendi `history` listesi değil:** Birden fazla kaynak olduğunda (R1, R2, R3...) her birinin ayrı bir geçmiş listesi olsaydı, "tüm sistemde zaman sırasıyla ne oldu" sorusuna cevap vermek için bu listeleri sonradan birleştirip sıralamak gerekirdi. Tek merkezi `EventLog`, tüm kaynaklar arasında **ortak bir zaman çizelgesi** sağlıyor.

`Resource`, `event_log`'u **opsiyonel** bir parametre olarak alıyor (`event_log=None` varsayılan). Bu, geriye dönük uyumluluk için önemli: log istemeyen biri (örn. sade bir hafta 2 testi) hiçbir şeyi değiştirmeden `Resource("R1")` yazmaya devam edebiliyor.

### 6) `scenarios/*.json` ve `src/scenario_loader.py` — senaryo dosyasından yükleme
Şimdiye kadar process/kaynak oluşturma ve olayları (acquire/release) Python kodunun içine gömerek yazıyorduk. Bu, her yeni test senaryosu için kodu değiştirmek anlamına gelir. Bunun yerine senaryoyu **veri** (JSON) olarak dışarı aldık:

```json
{
    "resources": [{"name": "R1", "total_instances": 3}],
    "events": [
        {"action": "acquire", "process": "P1", "resource": "R1", "amount": 2},
        {"action": "acquire", "process": "P2", "resource": "R1", "amount": 2},
        {"action": "release", "process": "P1", "resource": "R1", "amount": 1}
    ]
}
```

`load_scenario(path)` bu dosyayı okuyup `Resource` nesnelerini kurar, `events` listesindeki her adımı sırayla çalıştırır, process'leri **ilk geçtikleri event'te otomatik oluşturur** (ayrıca bir "processes" listesi tanımlamaya gerek yok — daha az tekrar).

**Neden bu önemli:** İleride (hafta 10 "Test ve İyileştirme") normal çalışma, tek deadlock, çoklu deadlock ve recovery senaryolarını test edeceğiz. Kod değişmeden, sadece yeni bir `.json` dosyası ekleyerek yeni senaryolar deneyebileceğiz.

İki örnek senaryo eklendi:
- `scenarios/hafta2_temel_akis.json` — hafta 2'deki temel akışın JSON hâli
- `scenarios/hafta3_cok_ornekli.json` — çok örnekli kaynak + bekleyen isteğin sonradan karşılanması

### 7) `src/state_table.py` ve `src/run_scenario.py`
`print_state_table()`, tüm process ve kaynakların anlık durumunu okunabilir bir tablo halinde konsola basıyor — planın istediği "durum tablosu" çıktısı bu.

`run_scenario.py`, komut satırından bir senaryo dosyası verip çalıştırmayı sağlıyor; olay kaydını, durum tablosunu ve HTML görselleştirmeyi (hafta 2'de eklediğimiz `html_view.py`, artık çok örnekli kaynakları da gösterecek şekilde güncellendi) tek seferde üretiyor:
```bash
python -m src.run_scenario scenarios/hafta3_cok_ornekli.json
```

**Adım adım görselleştirme:** `run_scenario.py`, `scenario_loader.py`'daki `load_scenario()` fonksiyonunu kullanmak yerine kendi içinde `run_scenario_step_by_step()` fonksiyonuyla senaryoyu event event işliyor ve her adımdan sonra bir HTML "kart seti" üretiyor (hafta 2'deki `simulation.py` mantığının aynısı). Bunu bilerek **ayrı bir fonksiyonda** tuttuk: `load_scenario()` testler ve basit kullanım için "senaryoyu çalıştır, son durumu ver" işini yapar; adım adım görselleştirme ayrı bir sorumluluk olduğu için ayrı bir yerde durur — biri değişince diğeri bozulmaz.

### 8) Testler
17 birim test yazıldı ve `pytest` ile doğrulandı:
- `tests/test_week2_simulation.py` (5) — yeni API'ye güncellendi, hafta 2 davranışı korunuyor
- `tests/test_week3_multi_instance.py` (5) — çok örnekli kaynak, tüm-ya-da-hiç kuralı, kuyruk atlama, hatalı release
- `tests/test_week3_event_log.py` (4) — olayların doğru sırayla ve doğru bilgiyle kaydedildiği
- `tests/test_week3_scenario_loader.py` (3) — JSON senaryolarının doğru çalıştığı

← [[00-Genel/11 Haftalık Plan]]
