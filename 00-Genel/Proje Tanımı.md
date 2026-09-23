---
tags: [deadlock-guardian, tanim]
---
# Proje Tanımı

**Tam ad:** Deadlock Guardian — Deadlock Risk Detection, Detection & Recovery System

| | |
|---|---|
| **Amaç** | Programların kaynakları kullanırken birbirini kilitlemesini (deadlock) önceden fark etmek, gerçekleştiğinde tespit etmek ve sistemin toparlanması için çözüm sunmak. |
| **Hedef** | Tek bir algoritma yazmak değil; deadlock yönetimini kullanıcıya anlaşılır biçimde gösteren, çalışan bir sistem geliştirmek. |

## Deadlock nedir?
Birden fazla process'in birbirinin tuttuğu kaynağı beklemesi ve hiçbirinin ilerleyememesi.

| Process | Elindeki | Beklediği |
|---|---|---|
| P1 | R1 | R2 |
| P2 | R2 | R1 |

Grafikte `P1 → R2 → P2 → R1 → P1` döngüsü oluşur. Döngü varsa deadlock var demektir.

## 3 ana aşama
1. **Risk Analizi:** deadlock oluşmadan önce tehlikeli bir durum varsa kullanıcıyı uyarır.
2. **Deadlock Tespiti:** kilitlenme olduğunda hangi process ve kaynakların sebep olduğunu bulur (Resource Allocation Graph + cycle detection).
3. **Recovery:** sistemi tekrar güvenli hale getirmek için çözüm seçenekleri sunar (örneğin bir process'i sonlandırıp kaynaklarını serbest bırakmak).

## Genel yapı
```
Process'ler (kaynak ister / bırakır)
        ↓
Deadlock Guardian (tüm ilişkileri takip eder)
        ↓                 ↓
  Risk Analizi     Deadlock Detection
        ↓                 ↓
      Uyarı            Recovery
```

## Kullanıcının göreceği ekran (taslak)
- Özet: aktif process sayısı, kaynak sayısı, deadlock riski (örn. "Yüksek")
- Process durumu: P1 Çalışıyor, P2 Bekliyor…
- Kaynak durumu: R1 → P1, R3 → Boş…
- Uyarı: "P2 ve P4 karşılıklı kaynak bekliyor."

## Kullanılan OS konuları
| Konu | Projedeki karşılığı |
|---|---|
| Process | Çalışan programları temsil eder |
| Resource | Process'lerin istediği kaynaklar |
| Resource Allocation | Hangi process'in hangi kaynağı aldığının takibi |
| Deadlock | Process'lerin birbirini bekleyip ilerleyemediği durum |
| Resource Allocation Graph | Process-kaynak ilişkilerinin grafiği |
| Cycle Detection | Grafikte döngü aranması |
| Banker's Algorithm | Kaynak verildiğinde sistemin güvenli durumda kalıp kalmayacağının kontrolü |
| Recovery | Deadlock sonrası güvenli duruma dönüş |
| Synchronization | Kaynak ve kilit mantığı |

## Kapsam kararı
> [!important] İlk sürümde gerçek bilgisayardaki process'ler yönetilmeyecek.
> Process ve resource senaryoları kontrollü bir **simülasyon ortamında** oluşturulacak. Gerçek sistem entegrasyonu daha sonra ek özellik olabilir.

← [[00-Genel/Proje Ana Sayfa]]
