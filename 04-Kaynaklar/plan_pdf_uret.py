"""Deadlock Guardian — 11 haftalık proje planı PDF'ini üretir."""
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (KeepTogether, Paragraph, SimpleDocTemplate,
                                Spacer, Table, TableStyle, PageBreak)

FONT_DIR = "/System/Library/Fonts/Supplemental/"
pdfmetrics.registerFont(TTFont("A", FONT_DIR + "Arial.ttf"))
pdfmetrics.registerFont(TTFont("AB", FONT_DIR + "Arial Bold.ttf"))
pdfmetrics.registerFontFamily("A", normal="A", bold="AB")

NAVY = colors.HexColor("#1B3A5C")
LINE = colors.HexColor("#B8C4D0")
ZEBRA = colors.HexColor("#F3F6F9")

title = ParagraphStyle("t", fontName="AB", fontSize=20, leading=24, alignment=TA_CENTER)
sub = ParagraphStyle("s", fontName="A", fontSize=10.5, leading=14, alignment=TA_CENTER,
                     textColor=colors.HexColor("#555555"), spaceBefore=3, spaceAfter=8)
h = ParagraphStyle("h", fontName="AB", fontSize=12.5, leading=16, textColor=NAVY,
                   spaceBefore=7, spaceAfter=4)
body = ParagraphStyle("b", fontName="A", fontSize=9.8, leading=13.4, spaceAfter=3)
cell = ParagraphStyle("c", fontName="A", fontSize=8.8, leading=11.8)
cellb = ParagraphStyle("cb", parent=cell, fontName="AB")
head_cell = ParagraphStyle("hc", parent=cellb, textColor=colors.white)


def table(rows, widths, header=True):
    data = [[Paragraph(c, head_cell if header and i == 0 else cell) for c in r]
            for i, r in enumerate(rows)]
    t = Table(data, colWidths=widths, repeatRows=1 if header else 0)
    style = [
        ("BOX", (0, 0), (-1, -1), 0.6, LINE),
        ("INNERGRID", (0, 0), (-1, -1), 0.3, LINE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("ROWBACKGROUNDS", (0, 1 if header else 0), (-1, -1), [colors.white, ZEBRA]),
    ]
    if header:
        style.append(("BACKGROUND", (0, 0), (-1, 0), NAVY))
    t.setStyle(TableStyle(style))
    return t


def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("A", 8)
    canvas.setFillColor(colors.HexColor("#777777"))
    canvas.drawString(1.7 * cm, 1 * cm, "Deadlock Guardian — İşletim Sistemleri Dersi Proje Planı")
    canvas.drawRightString(A4[0] - 1.7 * cm, 1 * cm, f"Sayfa {doc.page}")
    canvas.restoreState()


W = A4[0] - 3.4 * cm
story = [
    Paragraph("DEADLOCK GUARDIAN", title),
    Paragraph("Deadlock Risk Analizi, Tespiti ve Kurtarma Sistemi<br/>"
              "İşletim Sistemleri Dersi — 11 Haftalık Proje Planı", sub),
    table([
        ["<b>Öğrenci Adı Soyadı</b>", "<b>Öğrenci No</b>", "<b>Projedeki Görevi</b>"],
        ["", "", "Simülasyon ve veri modeli"],
        ["", "", "Deadlock tespiti ve recovery"],
        ["", "", "Risk analizi (Banker's Algorithm, risk seviyeleri)"],
        ["", "", "Arayüz ve görselleştirme"],
    ], [0.42 * W, 0.22 * W, 0.36 * W]),
    Spacer(1, 4),
    Paragraph("Ders Sorumlusu: ______________________ &nbsp;&nbsp;&nbsp; Teslim Tarihi: ____ / ____ / ________", body),

    Paragraph("1. Projenin Amacı", h),
    Paragraph(
        "Bir işletim sisteminde birden fazla process aynı kaynakları (dosya, cihaz, kilit, bellek bölgesi) "
        "kullanmak ister. Bir process elindeki kaynağı bırakmadan başka bir process'in tuttuğu kaynağı "
        "beklerse ve bu bekleme karşılıklı hale gelirse hiçbir process ilerleyemez; bu duruma "
        "<b>deadlock (kilitlenme)</b> denir.", body),
    Paragraph(
        "Deadlock Guardian, process ve kaynakları kontrollü bir simülasyon ortamında modelleyen bir yazılımdır. "
        "Sistem üç temel işi yerine getirir: <b>(1) Risk Analizi</b> — deadlock oluşmadan önce tehlikeli "
        "durumları belirleyip uyarır; <b>(2) Deadlock Tespiti</b> — kilitlenme oluştuğunda probleme dahil "
        "process ve kaynakları bulur; <b>(3) Recovery</b> — sistemi tekrar güvenli (SAFE) duruma getirmek "
        "için kurtarma seçenekleri sunar ve uygular. Amaç yalnızca bir algoritma yazmak değil, deadlock "
        "yönetimini kullanıcıya görsel ve anlaşılır biçimde sunan çalışan bir sistem geliştirmektir.", body),

    Paragraph("2. Kullanılacak İşletim Sistemi Konuları", h),
    Paragraph(
        "Process ve process durumları · Kaynak tahsisi (resource allocation) · Deadlock için gerekli dört koşul "
        "(mutual exclusion, hold and wait, no preemption, circular wait) · Resource Allocation Graph · "
        "Cycle detection · Çok örnekli kaynaklar için deadlock detection algoritması · Güvenli durum ve "
        "Banker's Algorithm · Deadlock recovery (process sonlandırma, kaynak geri alma) · Senkronizasyon ve "
        "kilit mantığı. <i>(Referans: Silberschatz, Galvin, Gagne — Operating System Concepts, 10. baskı, "
        "Bölüm 8: Deadlocks)</i>", body),

    Paragraph("3. 11 Haftalık Geliştirme Planı — Özet", h),
]

weeks = [
    ("1", "Konuyu Anlama ve Proje Tasarımı",
     "Deadlock konusunu kavramak ve projenin sınırlarını netleştirmek.",
     ["Deadlock, process, resource ve bekleme (waiting) kavramlarının incelenmesi",
      "Deadlock için gerekli dört koşulun öğrenilmesi: mutual exclusion, hold and wait, no preemption, circular wait",
      "Projenin modüllerinin belirlenmesi: simülasyon, tespit, risk analizi, kurtarma, arayüz",
      "Programlama dili ve araçların seçilmesi, ekip içi görev dağılımı",
      "GitHub deposunun ve proje klasör yapısının kurulması"],
     "Deadlock kavramı, dört koşul (Coffman koşulları)",
     "Proje tanım belgesi ve kurulmuş kod deposu"),
    ("2", "Basit Simülasyon",
     "Process ve kaynakların yazılımda modellendiği temel altyapıyı kurmak.",
     ["Process yapısının oluşturulması (kimlik, durum: RUNNING / WAITING / TERMINATED)",
      "Resource yapısının oluşturulması (kimlik, sahibi, bekleyen process kuyruğu)",
      "Kaynak isteme işlemi: kaynak boşsa process'e verilmesi",
      "Kaynak doluysa isteyen process'in WAITING durumuna alınıp kuyruğa eklenmesi",
      "Kaynak bırakıldığında sıradaki bekleyen process'e verilmesi",
      "Örnek: P1 → R1 alır, P2 → R1 ister ve bekler, P1 → R1'i bırakır, R1 → P2'ye geçer"],
     "Process durumları, kaynak tahsisi, bekleme kuyrukları",
     "Konsolda çalışan temel simülasyon (bu hafta deadlock tespiti yapılmaz)"),
    ("3", "Kaynak İlişkilerinin Takibi",
     "Sistemin herhangi bir andaki tam durumunu kayıt altında tutmak.",
     ["Hangi process'in hangi kaynağı tuttuğunu gösteren Allocation tablosunun tutulması",
      "Hangi process'in hangi kaynağı beklediğini gösteren Request tablosunun tutulması",
      "Birden fazla örneği olan kaynak desteği (örn. 3 adet yazıcı)",
      "Her işlemin zaman damgasıyla olay kaydına (log) yazılması",
      "Test senaryolarının JSON dosyasından yüklenebilmesi"],
     "Available / Allocation / Request veri yapıları",
     "Senaryo dosyasıyla çalışan sistem ve anlık durum tablosu"),
    ("4", "Deadlock Tespiti (Detection)",
     "Oluşan deadlock'u otomatik olarak bulmak.",
     ["Process ve kaynaklardan Resource Allocation Graph (RAG) oluşturulması",
      "DFS algoritması ile grafikte döngü (cycle) aranması",
      "Çok örnekli kaynaklar için deadlock detection algoritmasının uygulanması",
      "Deadlock'a dahil olan process ve kaynakların listelenmesi",
      "Doğru çalıştığını kanıtlayan birim testlerinin yazılması"],
     "Resource Allocation Graph, cycle detection, detection algoritması",
     "Deadlock'u tespit edip raporlayan modül ve testleri"),
    ("5", "Görselleştirme",
     "Process-kaynak ilişkilerini kullanıcının bir bakışta anlayacağı şekilde göstermek.",
     ["Process'lerin (daire) ve kaynakların (kare) graf üzerinde çizilmesi",
      "Tutma (kaynak → process) ve bekleme (process → kaynak) kenarlarının ayrı gösterilmesi",
      "Deadlock döngüsünün kırmızı renkle vurgulanması",
      "Simülasyon ilerledikçe grafiğin güncellenmesi"],
     "Resource Allocation Graph gösterimi",
     "Canlı güncellenen graf ekranı"),
    ("6", "Risk Analizi",
     "Deadlock oluşmadan önce tehlikeyi fark etmek (önleme yaklaşımı).",
     ["Güvenli durum (safe state) kavramının uygulanması",
      "Banker's Algorithm ile sistemin güvenli sırasının (safe sequence) hesaplanması",
      "Bir kaynak isteği karşılanmadan önce sistemin güvensiz duruma düşüp düşmeyeceğinin kontrolü",
      "Güvensiz durumda kullanıcıya uyarı verilmesi"],
     "Safe state, Banker's Algorithm, deadlock avoidance",
     "Güvenli / güvensiz durum uyarıları"),
    ("7", "Risk Seviyesi Sistemi",
     "Riski derecelendirip nedenini açıklamak.",
     ["Risk puanlama kurallarının belirlenmesi (bekleme zincirleri, boş kaynak oranı, güvenli durum sonucu)",
      "Riskin Low, Medium, High ve Critical seviyelerine ayrılması",
      "Riskin neden yükseldiğinin açıklanması (örn. \"P2 ve P4 karşılıklı kaynak bekliyor\")",
      "Risk seviyesinin zaman içindeki değişiminin kaydedilmesi"],
     "Kaynak kullanım analizi, güvensiz durum göstergeleri",
     "Risk göstergesi ve açıklamalar"),
    ("8", "Recovery (Kurtarma)",
     "Oluşan deadlock'tan sonra sistemi tekrar güvenli duruma getirmek.",
     ["Yöntem 1 — Process sonlandırma: döngüdeki bir process'in sonlandırılıp kaynaklarının serbest bırakılması",
      "Yöntem 2 — Kaynak geri alma (preemption): bir process'ten kaynağın alınıp başkasına verilmesi",
      "Kurban seçimi: en düşük maliyetli process'in (öncelik, tuttuğu kaynak sayısı) belirlenmesi",
      "Kurtarma sonrası tespitin tekrar çalıştırılıp sistemin SAFE olduğunun doğrulanması"],
     "Deadlock recovery, process termination, resource preemption",
     "Çalışan kurtarma modülü"),
    ("9", "Kullanıcı Arayüzü",
     "Tüm modülleri tek bir ekranda birleştirmek.",
     ["Dashboard: aktif process sayısı, kaynak sayısı, anlık risk seviyesi",
      "Process ve kaynak listeleri ile durumları",
      "Graf ekranı, deadlock uyarısı ve recovery seçenekleri",
      "Arayüzden process/kaynak ekleme, kaynak isteme ve bırakma"],
     "Tüm modüllerin entegrasyonu",
     "Bütünleşik ve kullanılabilir arayüz"),
    ("10", "Test ve İyileştirme",
     "Sistemin farklı durumlarda doğru ve kararlı çalıştığını göstermek.",
     ["Senaryo 1 — Normal çalışma: deadlock oluşmamalı",
      "Senaryo 2 — Tek deadlock: doğru tespit edilmeli",
      "Senaryo 3 — Birden fazla deadlock: hepsi ayrı ayrı bulunmalı",
      "Senaryo 4 — Recovery: sistem SAFE duruma dönmeli",
      "Bulunan hataların düzeltilmesi ve kodun düzenlenmesi"],
     "Doğrulama ve test",
     "Test raporu ve kararlı sürüm"),
    ("11", "Final Hazırlığı",
     "Projeyi baştan sona çalışır halde sunmak.",
     ["Son hata kontrolleri",
      "Demo senaryosunun hazırlanması ve prova edilmesi",
      "Proje raporunun yazılması",
      "Sunumun hazırlanması"],
     "Tüm konuların bütün halinde gösterimi",
     "Final demo, proje raporu ve sunum"),
]

label = ParagraphStyle("lbl", parent=cell, fontName="AB", textColor=NAVY)
bullet = ParagraphStyle("bul", parent=cell, leftIndent=10, bulletIndent=0, spaceAfter=1.5)
week_head = ParagraphStyle("wh", fontName="AB", fontSize=10.5, leading=13, textColor=colors.white)


def week_block(no, name, goal, items, topic, output):
    inner = [Paragraph(f"<b>Amaç:</b> {goal}", cell), Spacer(1, 3),
             Paragraph("Yapılacaklar", label)]
    inner += [Paragraph(i, bullet, bulletText="•") for i in items]
    inner += [Spacer(1, 3),
              Paragraph(f"<b>İlgili konu:</b> {topic}", cell),
              Paragraph(f"<b>Haftanın çıktısı:</b> {output}", cell)]
    t = Table([[Paragraph(f"HAFTA {no} — {name.upper()}", week_head)], [inner]], colWidths=[W])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("BACKGROUND", (0, 1), (-1, 1), colors.white),
        ("BOX", (0, 0), (-1, -1), 0.6, LINE),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    return KeepTogether([t, Spacer(1, 7)])


summary = [["Hafta", "Aşama", "Haftanın Çıktısı"]]
summary += [[w[0], f"<b>{w[1]}</b>", w[5]] for w in weeks]
story.append(Paragraph("Aşağıdaki özet tablo haftaların sırasını, sonraki sayfalar ise her haftanın "
                       "ayrıntılı iş listesini göstermektedir.", body))
story.append(table(summary, [0.08 * W, 0.38 * W, 0.54 * W]))
story.append(PageBreak())
story.append(Paragraph("4. Haftalık Ayrıntılı Plan", h))
for w in weeks:
    story.append(week_block(*w))

story += [
    KeepTogether([
        Paragraph("5. Kullanılacak Teknolojiler", h),
        table([
            ["Katman", "Teknoloji", "Kullanım Amacı"],
            ["Simülasyon ve algoritmalar", "Python", "Process/kaynak modeli, detection, Banker's ve recovery algoritmaları"],
            ["Arayüz", "PyQt veya web tabanlı arayüz", "Dashboard, graf görselleştirme ve kullanıcı etkileşimi"],
            ["Veri", "JSON / SQLite", "Senaryoların ve sonuçların saklanması"],
            ["Ekip çalışması", "Git + GitHub", "Kod paylaşımı ve sürüm takibi"],
        ], [0.27 * W, 0.28 * W, 0.45 * W]),
    ]),
    KeepTogether([
        Paragraph("6. Final Demo Senaryosu", h),
        Paragraph(
            "Sistem açılır → process ve kaynaklar oluşturulur → kaynaklar dağıtılır → karşılıklı bekleme "
            "senaryosu oluşturulur → sistem risk artışını gösterir → deadlock oluşur ve tespit edilir → "
            "probleme dahil process ve kaynaklar gösterilir → recovery seçenekleri sunulur → bir process "
            "sonlandırılıp kaynakları serbest bırakılır → sistem tekrar SAFE durumuna geçer.", body),
    ]),
    KeepTogether([
        Paragraph("7. Başarı Kriterleri", h),
        Paragraph(
            "• Deadlock senaryolarının doğru tespit edilmesi ve dahil olan process/kaynakların gösterilmesi<br/>"
            "• Deadlock oluşmadan önce risk uyarısı verilmesi<br/>"
            "• En az bir recovery yönteminin uygulanması ve sistemin güvenli duruma döndüğünün gösterilmesi<br/>"
            "• Normal ve deadlock durumlarının karşılaştırılabilmesi<br/>"
            "• Kodun ekip üyelerinin bağımsız çalışabileceği şekilde modüler olması<br/>"
            "• Finalde baştan sona çalışan bir demo sunulması", body),
    ]),
]

doc = SimpleDocTemplate(
    str(Path(__file__).parent / "Deadlock_Guardian_11_Haftalik_Plan.pdf"),
    pagesize=A4, leftMargin=1.7 * cm, rightMargin=1.7 * cm, topMargin=1.5 * cm, bottomMargin=1.6 * cm,
    title="Deadlock Guardian — 11 Haftalık Proje Planı")
doc.build(story, onFirstPage=footer, onLaterPages=footer)
print("ok")
