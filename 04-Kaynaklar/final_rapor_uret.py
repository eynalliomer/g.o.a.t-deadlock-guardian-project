"""Deadlock Guardian — final proje raporu PDF'ini üretir (el kitabı 11.2'deki bölümler).

    python 04-Kaynaklar/ekran_goruntusu_al.py   # önce görseller (kod değiştiyse)
    python 04-Kaynaklar/final_rapor_uret.py
"""
from pathlib import Path

from reportlab.graphics.shapes import Drawing, Line, Polygon, Rect, String
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, Frame, Image, KeepTogether, PageBreak, PageTemplate,
                                Paragraph, Preformatted, Spacer, Table, TableStyle)
from reportlab.platypus.tableofcontents import TableOfContents

HERE = Path(__file__).parent
IMG = HERE / "rapor_gorselleri"

FD = "/System/Library/Fonts/Supplemental/"
for name, f in [("A", "Arial.ttf"), ("AB", "Arial Bold.ttf"), ("AI", "Arial Italic.ttf"),
                ("M", "Courier New.ttf")]:
    pdfmetrics.registerFont(TTFont(name, FD + f))
pdfmetrics.registerFontFamily("A", normal="A", bold="AB", italic="AI", boldItalic="AB")

NAVY = colors.HexColor("#1B3A5C")
LINE = colors.HexColor("#B8C4D0")
ZEBRA = colors.HexColor("#F3F6F9")
GREY = colors.HexColor("#555555")
BOX = {
    "tanim": ("Tanım", colors.HexColor("#2E6DA4"), colors.HexColor("#EEF4FA")),
    "karar": ("Tasarım kararı", colors.HexColor("#6C3483"), colors.HexColor("#F5EEF8")),
    "sonuc": ("Sonuç", colors.HexColor("#2E8B57"), colors.HexColor("#EEF7F1")),
    "dikkat": ("Sınırlama", colors.HexColor("#D68910"), colors.HexColor("#FDF5E8")),
}
W = A4[0] - 3.6 * cm

st = {
    "cover": ParagraphStyle("cover", fontName="AB", fontSize=30, leading=36, alignment=TA_CENTER, textColor=NAVY),
    "coversub": ParagraphStyle("cs", fontName="A", fontSize=13, leading=19, alignment=TA_CENTER, textColor=GREY),
    "h1": ParagraphStyle("h1", fontName="AB", fontSize=18, leading=23, textColor=NAVY, spaceAfter=10),
    "h2": ParagraphStyle("h2", fontName="AB", fontSize=13, leading=17, textColor=NAVY, spaceBefore=10,
                         spaceAfter=4, keepWithNext=1),
    "p": ParagraphStyle("p", fontName="A", fontSize=10, leading=14.5, spaceAfter=5),
    "cell": ParagraphStyle("c", fontName="A", fontSize=8.9, leading=11.8),
    "cellh": ParagraphStyle("ch", fontName="AB", fontSize=8.9, leading=11.8, textColor=colors.white),
    "boxt": ParagraphStyle("bt", fontName="AB", fontSize=9.5, leading=12.5),
    "boxp": ParagraphStyle("bp", fontName="A", fontSize=9.6, leading=13.6, spaceAfter=2),
    "bul": ParagraphStyle("bul", fontName="A", fontSize=10, leading=14, leftIndent=12, bulletIndent=2, spaceAfter=2),
    "code": ParagraphStyle("code", fontName="M", fontSize=8.4, leading=10.8),
    "cap": ParagraphStyle("cap", fontName="AI", fontSize=8.5, leading=11, alignment=TA_CENTER, textColor=GREY,
                          spaceAfter=10),
    "toc0": ParagraphStyle("toc0", fontName="A", fontSize=10.5, leading=17),
}


class Chapter(Paragraph):
    """İçindekiler tablosuna kaydolan bölüm başlığı."""


def H1(title):
    return [PageBreak(), Chapter(title, st["h1"])]


def H2(t): return Paragraph(t, st["h2"])
def P(t): return Paragraph(t, st["p"])
def B(items): return [Paragraph(i, st["bul"], bulletText="•") for i in items]


def Box(kind, content):
    label, edge, bg = BOX[kind]
    inner = [Paragraph(label, ParagraphStyle("x", parent=st["boxt"], textColor=edge))]
    inner += [Paragraph(c, st["boxp"]) for c in (content if isinstance(content, list) else [content])]
    t = Table([["", inner]], colWidths=[4, W - 4])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, 0), edge), ("BACKGROUND", (1, 0), (1, 0), bg),
        ("LEFTPADDING", (0, 0), (0, 0), 0), ("RIGHTPADDING", (0, 0), (0, 0), 0),
        ("LEFTPADDING", (1, 0), (1, 0), 9), ("RIGHTPADDING", (1, 0), (1, 0), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    return KeepTogether([t, Spacer(1, 7)])


def Code(text):
    t = Table([[Preformatted(text.strip("\n"), st["code"])]], colWidths=[W])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F4F4F4")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#DDDDDD")),
        ("LEFTPADDING", (0, 0), (-1, -1), 8), ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    return KeepTogether([t, Spacer(1, 7)])


def T(rows, widths, min_rows_height=None):
    data = [[Paragraph(str(c), st["cellh"] if i == 0 else st["cell"]) for c in r] for i, r in enumerate(rows)]
    t = Table(data, colWidths=[w * W for w in widths], repeatRows=1,
              rowHeights=None if min_rows_height is None else [None] + [min_rows_height] * (len(rows) - 1))
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("BOX", (0, 0), (-1, -1), 0.6, LINE), ("INNERGRID", (0, 0), (-1, -1), 0.3, LINE),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, ZEBRA]),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5), ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 3.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
    ]))
    return KeepTogether([t, Spacer(1, 8)])


def Fig(name, caption, width=W):
    path = IMG / f"{name}.png"
    img = Image(str(path))
    ratio = img.imageHeight / img.imageWidth
    img.drawWidth, img.drawHeight = width, width * ratio
    frame = Table([[img]], colWidths=[width])
    frame.setStyle(TableStyle([("BOX", (0, 0), (-1, -1), 0.5, LINE),
                               ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                               ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 0)]))
    return KeepTogether([frame, Spacer(1, 3), Paragraph(caption, st["cap"])])


def fig_architecture():
    """Katmanlı mimari: arayüz → motor → algoritmalar → veri modeli."""
    d = Drawing(W, 250)
    layers = [
        (200, "ARAYÜZ (View + Controller)", "app.py · dashboard_view.py · graph_view.py · html_view.py · run_scenario.py",
         colors.HexColor("#EEF4FA"), colors.HexColor("#2E6DA4")),
        (145, "MOTOR (Model)", "engine.py — Simulation: durum, eylemler, geri al (event sourcing)",
         colors.HexColor("#F5EEF8"), colors.HexColor("#6C3483")),
        (90, "ALGORİTMALAR", "detection.py · bankers.py · risk.py · recovery.py",
         colors.HexColor("#EEF7F1"), colors.HexColor("#2E8B57")),
        (35, "VERİ MODELİ", "process.py · resource.py · event_log.py  +  scenarios/*.json",
         colors.HexColor("#FDF5E8"), colors.HexColor("#B9770E")),
    ]
    for y, title, files, bg, edge in layers:
        d.add(Rect(10, y, W - 20, 40, rx=6, ry=6, fillColor=bg, strokeColor=edge, strokeWidth=1.3))
        d.add(String(W / 2, y + 24, title, fontName="AB", fontSize=10.5, textAnchor="middle", fillColor=edge))
        d.add(String(W / 2, y + 9, files, fontName="A", fontSize=8.5, textAnchor="middle"))
    for y in (200, 145, 90):  # üst katman alttakini çağırır
        x = W / 2
        d.add(Line(x, y, x, y - 13, strokeColor=GREY, strokeWidth=1.2))
        d.add(Polygon([x, y - 15, x - 4, y - 8, x + 4, y - 8], fillColor=GREY, strokeColor=GREY))
    d.add(String(W / 2, 12, "Her katman yalnızca altındakini çağırır; motor ekranı, algoritmalar motoru bilmez.",
                 fontName="AI", fontSize=8.5, textAnchor="middle", fillColor=GREY))
    return d


class Doc(BaseDocTemplate):
    def __init__(self, path):
        super().__init__(path, pagesize=A4, leftMargin=1.8 * cm, rightMargin=1.8 * cm,
                         topMargin=1.7 * cm, bottomMargin=1.7 * cm,
                         title="Deadlock Guardian — Proje Raporu", author="Deadlock Guardian")
        frame = Frame(self.leftMargin, self.bottomMargin, self.width, self.height, id="f")
        self.addPageTemplates([PageTemplate(id="p", frames=[frame], onPage=self.footer)])

    def footer(self, c, doc):
        if doc.page == 1:
            return
        c.saveState()
        c.setFont("A", 8)
        c.setFillColor(colors.HexColor("#777777"))
        c.drawString(1.8 * cm, 1 * cm, "Deadlock Guardian — Proje Raporu")
        c.drawRightString(A4[0] - 1.8 * cm, 1 * cm, f"Sayfa {doc.page}")
        c.restoreState()

    def afterFlowable(self, f):
        if isinstance(f, Chapter):
            self.notify("TOCEntry", (0, f.getPlainText(), self.page))


# ============================================================
story = [
    Spacer(1, 4.5 * cm),
    Paragraph("DEADLOCK GUARDIAN", st["cover"]), Spacer(1, 10),
    Paragraph("Deadlock Risk Analizi, Tespiti ve Kurtarma Sistemi",
              ParagraphStyle("c2", parent=st["coversub"], fontName="AB", fontSize=15, textColor=colors.black)),
    Spacer(1, 10),
    Paragraph("Proje Raporu", st["coversub"]),
    Spacer(1, 3.5 * cm),
    Paragraph("İşletim Sistemleri Dersi · Yazılım Mühendisliği Bölümü", st["coversub"]),
    Spacer(1, 6),
    Paragraph("Ana kaynak: Silberschatz, Galvin, Gagne — <i>Operating System Concepts</i>, 10. baskı, Bölüm 8",
              st["coversub"]),
    Spacer(1, 6),
    Paragraph("Kaynak kod: github.com/eynalliomer/g.o.a.t-deadlock-guardian-project", st["coversub"]),
    Spacer(1, 2 * cm),
    Paragraph("Hazırlayanlar: ..............................................................", st["coversub"]),
]

toc = TableOfContents()
toc.levelStyles = [st["toc0"]]
story += [PageBreak(), Paragraph("İçindekiler", st["h1"]), toc]

# ============================================================
story += H1("1. Özet")
story += [
    P("Deadlock Guardian, process'lerin kaynak kullanımını izleyen, deadlock riskini oluşmadan önce "
      "değerlendiren, oluşan deadlock'u tespit eden ve sistemi yeniden güvenli duruma getirmek için kurtarma "
      "seçenekleri sunan bir işletim sistemi <b>simülasyonudur</b>. Gerçek işletim sistemi process'leri yerine "
      "kontrollü bir modelde çalışır; senaryolar JSON dosyalarıyla tanımlanır."),
    P("Sistem üç aşamadan oluşur: (1) <b>risk analizi</b>: Banker's Algorithm ile güvenli durum kontrolü ve "
      "LOW / MEDIUM / HIGH / CRITICAL risk seviyeleri; (2) <b>tespit</b>: Resource Allocation Graph (RAG) üzerinde "
      "DFS ile döngü arama ve çok örnekli kaynaklar için tespit algoritması; (3) <b>kurtarma</b>: maliyete göre "
      "kurban seçerek process sonlandırma ya da kaynak geri alma."),
    P("Proje Python ile geliştirildi ve Flask tabanlı bir web arayüzüyle sunuldu. Arayüzde senaryolar adım adım "
      "oynatılabiliyor, RAG canlı çiziliyor, deadlock anında kurtarma seçenekleri maliyetleriyle listeleniyor ve "
      "tek tıkla uygulanabiliyor. Sistem <b>140 otomatik testle</b> doğrulandı; kod kapsamı <b>%99</b>'dur. "
      "Banker's Algorithm ders kitabındaki örnekle birebir aynı sonuçları vermektedir."),
    T([["Ölçüt", "Değer"],
       ["Programlama dili / arayüz", "Python 3.14 / Flask web arayüzü"],
       ["Kaynak kod", "18 modül, yaklaşık 1600 satır (src/)"],
       ["Senaryo dosyası", "10 (normal, tek ve çoklu deadlock, güvensiz durum, kurtarma, final demo)"],
       ["Otomatik test / kod kapsamı", "140 test, hepsi geçiyor / %99"],
       ["Geliştirme süreci", "11 haftalık plan, her hafta Git etiketiyle (hafta-01 … hafta-11) işaretlendi"]],
      [0.35, 0.65]),
]

# ============================================================
story += H1("2. Giriş ve Problem Tanımı")
story += [
    P("Çok görevli bir işletim sisteminde process'ler sınırlı sayıdaki kaynağı (yazıcı, disk, kilit, bellek "
      "bölgesi) paylaşır. Bir process elindeki kaynağı bırakmadan başka bir kaynağı beklerken, o kaynak da ilk "
      "process'in kaynağını bekleyen başka bir process'in elindeyse, ikisi de sonsuza kadar bekler. Bu duruma "
      "<b>deadlock</b> (kilitlenme) denir."),
    Box("tanim", "<b>Deadlock:</b> Bir process kümesindeki her process'in, yine aynı kümedeki başka bir "
                 "process'in yol açabileceği bir olayı (genellikle kaynak bırakılmasını) beklemesi durumu "
                 "(Silberschatz, 8.2)."),
    P("Deadlock'un bedeli yüksektir: kilitlenen process'ler hiç ilerlemez, tuttukları kaynaklar başka process'lere "
      "de kapalı kalır ve sistem giderek yavaşlar. Gerçek sistemlerin çoğu deadlock'u görmezden gelir ve sorun "
      "çıktığında sistemin yeniden başlatılmasına güvenir; çünkü önleme ve kaçınma yöntemleri pahalıdır."),
    H2("2.1 Projenin amacı"),
    P("Deadlock Guardian'ın amacı, ders kitabında ayrı ayrı anlatılan deadlock kavramlarını <b>tek bir çalışan "
      "sistemde</b> birleştirmek ve deadlock'un oluşumunu, tespitini ve çözümünü görünür kılmaktır:"),
] + B([
    "Deadlock oluşmadan <b>önce</b> tehlikeyi fark edip kullanıcıyı uyarmak (risk analizi),",
    "Oluşan deadlock'u ve ona dahil process ile kaynakları <b>göstermek</b> (tespit),",
    "Deadlock'u en düşük maliyetle <b>çözmek</b> ve sistemin güvenli duruma döndüğünü doğrulamak (kurtarma),",
    "Bütün bunları adım adım izlenebilen, etkileşimli bir arayüzde sunmak.",
])

# ============================================================
story += H1("3. Teorik Arka Plan")
story += [
    H2("3.1 Deadlock'un dört gerekli koşulu (Coffman koşulları)"),
    P("Bir sistemde deadlock oluşabilmesi için aşağıdaki dört koşulun <b>aynı anda</b> sağlanması gerekir "
      "(Silberschatz, 8.3.1). Koşullardan biri bile kırılırsa deadlock oluşamaz."),
    T([["Koşul", "Anlamı", "Projedeki karşılığı"],
       ["Karşılıklı dışlama (mutual exclusion)", "Bir kaynak birimini aynı anda tek process kullanabilir",
        "Resource.allocation: her birim tek process'te"],
       ["Tut ve bekle (hold and wait)", "Process kaynak tutarken başka kaynak bekleyebilir",
        "Process elinde R1 varken R2'yi isteyip WAITING olabilir"],
       ["Geri alınamazlık (no preemption)", "Kaynak sahibinden zorla alınamaz",
        "Kaynak yalnızca release ile bırakılır (kurtarma hariç)"],
       ["Döngüsel bekleme (circular wait)", "P1 → P2 → … → Pn → P1 bekleme zinciri",
        "RAG'deki döngü (P1 → R2 → P2 → R1 → P1)"]],
      [0.28, 0.36, 0.36]),
    H2("3.2 Resource Allocation Graph (RAG)"),
    P("RAG, sistemin anlık durumunu gösteren yönlü bir graftır (Silberschatz, 8.3.2). Düğümler process'ler ve "
      "kaynaklardır. <b>İstek kenarı</b> P → R, process'in kaynağı beklediğini; <b>atama kenarı</b> R → P, "
      "kaynağın bir biriminin process'e verildiğini gösterir. Her kaynak tek örnekliyse grafta döngü olması "
      "deadlock olması demektir. Çok örnekli kaynaklarda ise döngü yalnızca <b>olası</b> bir deadlock'u "
      "gösterir: döngüdeki bir kaynağın başka bir birimi, kimseyi beklemeyen bir process'teyse o process "
      "bitince döngü çözülür."),
    H2("3.3 Tespit algoritması"),
    P("Çok örnekli kaynaklar için döngü aramak yetmediğinden ders kitabındaki tespit algoritması kullanılır "
      "(Silberschatz, 8.7.2). Algoritma, isteği mevcut boş kaynakla (<i>Work</i>) karşılanabilen bir process "
      "arar; bulursa o process'in işini bitirip kaynaklarını bırakacağını varsayar (<i>Work += Allocation</i>). "
      "Bu, yeni bir process bitemeyene kadar tekrarlanır; sonunda bitemeyen process'ler deadlock'tadır."),
    H2("3.4 Banker's Algorithm ve güvenli durum"),
    P("Banker's Algorithm (Dijkstra, 1965) deadlock'tan <b>kaçınma</b> yöntemidir (Silberschatz, 8.6.3). Her "
      "process baştan en fazla ne kadar kaynak isteyebileceğini (<i>Max</i>) bildirir. "
      "<i>Need = Max − Allocation</i>, process'in en kötü durumda daha isteyebileceği miktardır. Process'lerin "
      "her biri sırası geldiğinde <i>Need</i>'inin tamamını alıp bitirebileceği bir sıra (güvenli sıra) varsa "
      "sistem <b>güvenli durumdadır</b>. Bir istek, verildiğinde sistem güvenli kalacaksa verilir."),
    Box("tanim", ["<b>Güvensiz durum ≠ deadlock.</b> Deadlock olan her sistem güvensizdir; ama güvensiz bir "
                  "sistemde deadlock henüz oluşmamış olabilir. Güvensiz durum, deadlock'un artık garanti olarak "
                  "önlenemeyeceği anlamına gelir.",
                  "Tespit algoritması ile güvenlik algoritması aynı döngüyü kullanır; farkları talep tablosudur: "
                  "tespit <i>Request</i>'e (şu an beklenen), Banker's <i>Need</i>'e (en kötü durumda istenebilecek) "
                  "bakar."]),
    H2("3.5 Kurtarma (recovery)"),
    P("Deadlock oluştuktan sonra döngü zorla kırılmalıdır (Silberschatz, 8.8). İki yöntem vardır: "
      "<b>process sonlandırma</b> (deadlock'taki process'ler birer birer sonlandırılır, her seferinde tespit "
      "tekrar çalıştırılır) ve <b>kaynak geri alma</b> (bir process'in kaynağı alınıp bekleyene verilir; kaynağı "
      "alınan process geri sarılır, rollback). Her iki yöntemde de amaç <b>en düşük maliyetli kurbanı</b> "
      "seçmek ve aynı process'in sürekli kurban seçilmesini (starvation) önlemektir."),
]

# ============================================================
story += H1("4. Tasarım")
story += [
    H2("4.1 Katmanlı mimari"),
    P("Sistem, <b>sorumlulukların ayrılması</b> (separation of concerns) ilkesine göre dört katmana ayrıldı. "
      "Arayüz MVC (Model-View-Controller) yapısındadır: motor (Model) ekranı bilmez; aynı motoru hem komut satırı "
      "aracı hem web arayüzü kullanır. Algoritmalar arayüzden bağımsız olduğu için ayrı ayrı test edilebildi."),
    fig_architecture(),
    Paragraph("Şekil 1 — Deadlock Guardian'ın katmanlı mimarisi", st["cap"]),
    H2("4.2 Modüller"),
    T([["Katman", "Modül", "Sorumluluğu"],
       ["Veri modeli", "process.py", "Process: durum (READY/WAITING/TERMINATED), tuttuğu kaynaklar, Max, öncelik"],
       ["", "resource.py", "Resource: toplam/boş birim, dağıtım tablosu, bekleme kuyruğu, acquire/release"],
       ["", "event_log.py", "Bütün kaynaklar için ortak, zaman sıralı olay kaydı"],
       ["Algoritmalar", "detection.py", "RAG kurulumu, DFS ile döngü arama, tespit algoritması, deadlock raporu"],
       ["", "bankers.py", "Need, güvenlik algoritması, kaynak isteği algoritması (SAFE/UNSAFE/WAIT)"],
       ["", "risk.py", "LOW/MEDIUM/HIGH/CRITICAL risk seviyesi ve nedenleri"],
       ["", "recovery.py", "Kurtarma seçenekleri, maliyet formülü, sonlandırma, kaynak geri alma"],
       ["Motor", "engine.py", "Simulation: senaryoyu oynatma, elle eylem, analiz, geri al"],
       ["Arayüz", "app.py, dashboard_view.py", "Flask web arayüzü (Controller ve View)"],
       ["", "graph_view.py, html_view.py", "RAG'in SVG çizimi, kartlar, statik adım adım önizleme"],
       ["", "run_scenario.py", "Komut satırı aracı: senaryoyu oynatır, konsol raporu ve HTML üretir"]],
      [0.18, 0.27, 0.55]),
    H2("4.3 Veri yapıları"),
    P("Bütün tablolar Python sözlükleriyle tutuldu; bu, ders kitabındaki matrislerin (Allocation, Max, Need) "
      "kaynak adlarıyla okunabilir bir karşılığıdır:"),
    Code('''
resource.allocation   = {P1: 2, P3: 1}            # hangi process kaç birim tutuyor
resource.waiting_queue = [(P2, 1)]                # kim, kaç birim bekliyor
process.held_resources = {"R1": 2, "R2": 1}
process.max_claim      = {"R1": 2, "R2": 1}       # Banker's için bildirilen Max
rag                    = {"R1": ["P1"], "P2": ["R1"], ...}   # {düğüm: [komşular]}
'''),
    H2("4.4 Senaryo dosyası biçimi"),
    P("Senaryolar kod değiştirmeden yeni durumlar denenebilsin diye JSON dosyası olarak tanımlandı. "
      "<i>processes</i> bölümü isteğe bağlıdır; Max bildirilmezse Banker's analizi yapılmaz."),
    Code('''
{
  "resources": [{"name": "R1", "total_instances": 1}, {"name": "R3", "total_instances": 2}],
  "processes": [{"name": "P1", "max": {"R1": 1, "R3": 1}, "priority": 1}],
  "events": [
    {"action": "acquire", "process": "P1", "resource": "R1"},
    {"action": "release", "process": "P1", "resource": "R1"},
    {"action": "recover"}
  ]
}
'''),
    H2("4.5 Tasarım kararları"),
    T([["Karar", "Seçenek", "Gerekçe"],
       ["Kaynak isteme kuralı", "Tüm-ya-da-hiç", "İstenen miktarın tamamı verilemiyorsa process tamamen bekler; "
                                                 "Banker's modeliyle uyumlu"],
       ["Banker's davranışı", "Yalnızca uyarı", "Güvensiz istek engellenmez; kullanıcı riski görür ve deadlock'un "
                                               "nasıl oluştuğu izlenebilir"],
       ["Risk: MEDIUM", "Bekleme VEYA boş kaynak %20'nin altı", "LOW → MEDIUM geçişi erken ve net görünsün"],
       ["Kurtarma yöntemi", "Birer birer sonlandırma + kaynak geri alma", "Kitaptaki iki yöntem de gösterilsin; "
                                                                         "hepsini birden sonlandırmak gereksiz iş kaybı"],
       ["Kurban maliyeti", "öncelik×10 − serbest bırakılan birim×2 + kurban sayısı×5",
        "Önemli process korunur, çok kaynak açan seçenek ucuzdur, sık kurban seçilen pahalılaşır (starvation)"],
       ["Arayüz", "Flask web", "Hafta 5'ten beri yazılan HTML/SVG çizim kodu yeniden kullanıldı"],
       ["Veri", "JSON senaryo dosyaları", "Okunabilir, sürüm kontrolüne uygun, ek kurulum gerektirmez"]],
      [0.2, 0.3, 0.5]),
]

# ============================================================
story += H1("5. Gerçekleştirme")
story += [
    H2("5.1 Döngü arama: DFS ve üç renk"),
    P("Her düğüm beyaz (ziyaret edilmedi), gri (şu anki yolun üstünde) ya da siyah (bitti) olarak işaretlenir. "
      "Gri bir düğüme yeniden ulaşmak, yolun kendisine geri dönmesi, yani döngüdür. Siyah düğümler bir daha "
      "taranmadığı için algoritma O(V + E) zamanda çalışır. Birden fazla bağımsız deadlock olduğunda bulunan "
      "döngünün düğümleri graftan çıkarılıp arama tekrarlanır (<i>find_cycles</i>)."),
    Code('''
def dfs(node):
    color[node] = GRAY
    path.append(node)
    for neighbor in graph[node]:
        if color[neighbor] == GRAY:              # yoldaki düğüme geri döndük: döngü
            return path[path.index(neighbor):]
        if color[neighbor] == WHITE:
            cycle = dfs(neighbor)
            if cycle:
                return cycle
    color[node] = BLACK
    path.pop()
'''),
    H2("5.2 Tespit ve Banker's için ortak çekirdek"),
    P("Tespit algoritması ile Banker's güvenlik algoritması aynı Work/Finish döngüsünü kullandığı için döngü "
      "tek bir fonksiyona çıkarıldı; iki algoritma yalnızca farklı bir talep tablosu verir."),
    Code('''
def run_to_completion(work, demand, allocation, finished):
    # demand: tespitte Request, Banker's'ta Need
    while progress:
        for name in finished:
            if not finished[name] and all(n <= work[r] for r, n in demand[name].items()):
                for r, n in allocation[name].items():
                    work[r] += n                 # işini bitirir, kaynaklarını bırakır
                finished[name] = True
                order.append(name)
    return order, stuck                          # güvenli sıra, bitemeyenler
'''),
    H2("5.3 Kaynak isteği algoritması"),
    P("Bir istek gerçekleşmeden önce üç adımda değerlendirilir: (1) istek Need'i aşıyorsa hata; (2) boşta "
      "yeterli kaynak yoksa WAIT; (3) istek verilmiş gibi yapılıp oluşan durum güvenli mi diye bakılır: SAFE ya "
      "da UNSAFE. Değerlendirme gerçek durumu değiştirmez, kopyalar üzerinde çalışır."),
    H2("5.4 Risk seviyeleri"),
    P("Risk seviyesi, tetiklenen kuralların en yükseğidir; her kural kendi nedenini ekler. Böylece arayüz "
      "yalnızca \"HIGH\" demek yerine \"neden HIGH\" sorusunu da cevaplar."),
    T([["Seviye", "Koşul", "Örnek neden mesajı"],
       ["CRITICAL", "Tespit algoritması deadlock buldu", "DEADLOCK: P1, P2 takılı. Döngü: P1 → R2 → P2 → R1 → P1"],
       ["HIGH", "Banker's güvenli sıra bulamıyor", "Sistem güvensiz: Banker's güvenli sıra bulamıyor."],
       ["MEDIUM", "Bekleyen process var, boş kaynak %20'nin altında ya da döngü var ama deadlock yok",
        "P3 bekliyor: R3 (2 birim) şu an P1 elinde."],
       ["LOW", "Hiçbiri", "Sistem normal çalışıyor."]],
      [0.14, 0.4, 0.46]),
    H2("5.5 Kurtarma"),
    P("Deadlock'taki her process için bir \"sonlandır\" seçeneği, elindeki ve birinin beklediği her kaynak için "
      "bir \"geri al\" seçeneği üretilir ve maliyete göre sıralanır. Otomatik kurtarma en ucuz seçeneği uygular, "
      "tespiti tekrar çalıştırır ve deadlock bitene kadar sürer. Eşit maliyette kaynak geri alma önce gelir, "
      "çünkü process yaşamaya devam eder."),
    Code('''
def option_cost(process, freed_units):
    return process.priority * 10 - freed_units * 2 + process.victim_count * 5
'''),
    H2("5.6 Motor ve geri alma"),
    P("Motor, sistemin her durumunu \"başlangıç senaryosu + uygulanan eylemler listesi\" olarak tanımlar "
      "(event sourcing). Simülasyon deterministik olduğundan \"geri al\", baştan başlayıp son eylem hariç "
      "hepsini yeniden oynatmaktır; bir process sonlandırmasını geri almak bile ek kod gerektirmedi. Her eylem, "
      "durum değiştirilmeden <b>önce</b> doğrulanır; hatalı bir eylem sistemi yarım bırakmaz."),
    H2("5.7 Arayüz"),
    P("Web arayüzü tek sayfalık bir dashboard'dur: senaryo seçimi, adım ilerletme / geri alma / sıfırlama "
      "düğmeleri, risk seyri, özet kartları, durum paneli, kurtarma seçenekleri (her birinin yanında \"Uygula\" "
      "düğmesi), senaryo dışı elle eylem formu, RAG çizimi, process ve kaynak kartları ve olay akışı. Her düğme "
      "bir POST isteği gönderir ve sayfaya geri yönlendirilir; böylece sayfa yenilendiğinde aynı eylem iki kez "
      "uygulanmaz. Sunucu yalnızca yerel adreste (127.0.0.1) çalışır ve yalnızca senaryo klasöründeki dosyaları "
      "yükler."),
]

# ============================================================
story += H1("6. Test ve Sonuçlar")
story += [
    H2("6.1 Final demo senaryosu"),
    P("Final demo senaryosu (<i>scenarios/final_demo.json</i>) üç process ve üç kaynakla risk seviyesinin adım "
      "adım yükselişini, deadlock'u ve kurtarmayı gösterir:"),
    T([["Adım", "Olay", "Risk", "Banker's"],
       ["0", "Başlangıç", "LOW", "Güvenli"],
       ["1", "P1, R1'den 1 birim istiyor", "LOW", "SAFE"],
       ["2", "P1, R3'ten 1 birim istiyor", "LOW", "SAFE"],
       ["3", "P3, R3'ten 2 birim istiyor (boşta 1 var, bekler)", "MEDIUM", "WAIT"],
       ["4", "P2, R2'den 1 birim istiyor", "HIGH", "UNSAFE: uyarı"],
       ["5", "P1, R2'den 1 birim istiyor (bekler)", "HIGH", "WAIT"],
       ["6", "P2, R1'den 1 birim istiyor: P1 ile P2 birbirini bekliyor", "CRITICAL", "WAIT"],
       ["7", "Recovery: Sonlandır P1 (maliyet 6, önerilen)", "MEDIUM", "Güvenli (P2 → P3)"],
       ["8–10", "P2 ve P3 işini bitirip kaynakları bırakıyor", "LOW", "Güvenli"]],
      [0.08, 0.56, 0.14, 0.22]),
    P("Banker's Algorithm sistemin güvensiz duruma düştüğünü 4. adımda, yani deadlock oluşmadan <b>iki adım "
      "önce</b> bildirmektedir. Deadlock anında en ucuz seçenek P1'i sonlandırmaktır: P1 hem R1'i hem R3'ü "
      "tuttuğu için sonlandırılması 2 birim serbest bırakır."),
    Fig("03_high", "Şekil 2 — 4. adım (HIGH): P2'nin isteği sistemi güvensiz duruma soktu; henüz deadlock yok."),
    Fig("04_critical", "Şekil 3 — 6. adım (CRITICAL): P1 → R2 → P2 → R1 → P1 döngüsü kırmızıyla vurgulanıyor; "
                       "kurtarma seçenekleri maliyetleriyle listeleniyor."),
    Fig("05_recovery", "Şekil 4 — 7. adım: P1 sonlandırıldı (gri); R1 P2'ye, R3'ün iki birimi P3'e geçti; "
                       "Banker's yeniden güvenli sıra buluyor."),
    H2("6.2 Sistem testleri"),
    T([["No", "Senaryo", "Beklenen sonuç", "Gerçek sonuç"],
       ["1", "Normal çalışma", "Deadlock yok, risk LOW", "9 adımın hepsi LOW, her istek SAFE"],
       ["2", "Tek deadlock (P1-R1-P2-R2)", "P1 ve P2 deadlock'ta, CRITICAL", "Beklendiği gibi"],
       ["3", "Çoklu deadlock (iki ayrı döngü)", "İki döngü ayrı raporlanır", "İki döngü raporlandı; kurtarma "
                                                                           "ikisini iki adımda çözdü"],
       ["4", "Deadlock + kurtarma", "Deadlock kalmaz, sistem SAFE", "Beklendiği gibi"],
       ["5", "Döngü var ama deadlock yok", "Deadlock yok", "Risk en fazla MEDIUM, hiç CRITICAL değil"]],
      [0.06, 0.3, 0.3, 0.34]),
    Fig("06_coklu_deadlock", "Şekil 5 — Çoklu deadlock: iki bağımsız döngü ayrı ayrı raporlanıyor ve grafta "
                             "vurgulanıyor."),
    H2("6.3 Otomatik testler ve kod kapsamı"),
    P("Her hafta yazılan kod pytest ile test edildi; her hafta bütün önceki testler yeniden çalıştırıldı "
      "(regresyon). Toplam <b>140 test</b> var ve hepsi geçiyor; satır kapsamı <b>%99</b>'dur. Kapsam dışı kalan "
      "4 satır, programın yalnızca komut satırından doğrudan çalıştırıldığında devreye giren satırlar ve bir "
      "hata ayıklama metnidir."),
    T([["Test türü", "Örnek"],
       ["Birim", "DFS döngü arama, güvenlik algoritması, maliyet formülü, Türkçe ek seçimi"],
       ["Entegrasyon", "Senaryo + Banker's; motor + tespit + kurtarma + geri al"],
       ["Sistem", "Senaryo dosyaları baştan sona; web arayüzünün düğmeleri (Flask test istemcisi)"],
       ["Kitapla doğrulama", "Silberschatz 8.6.3.3: güvenli sıra &lt;P1, P3, P4, P0, P2&gt;; P1'in isteği SAFE, "
                             "ardından P4'ünki WAIT, P0'ınki UNSAFE"]],
      [0.22, 0.78]),
    KeepTogether([H2("6.4 Testlerle bulunan hatalar"), P("Uç durumlar sistematik olarak denendi; beş hata bulundu ve her biri için önce hatayı "
                    "gösteren bir test yazıldı, sonra hata düzeltildi:"), T([["Durum", "Hata", "Düzeltme"],
       ["Toplam adetten fazla istek", "Process sonsuza kadar bekliyor, tespit algoritması görmüyordu", "İstek reddediliyor"],
       ["Negatif / sıfır miktar", "Kaynak birimi \"üretiliyor\" ya da boş kayıt oluşuyordu", "Miktar en az 1 olmalı"],
       ["Bekleyen process'in eylemi", "Process iki kuyrukta birden duruyor, durumu yanlış görünüyordu",
        "Bekleyen process bloke durumda; eylem reddediliyor"],
       ["Senaryoda olmayan kaynak", "Web sayfası çöküyordu", "Anlaşılır hata mesajı"],
       ["İki bağımsız deadlock", "Raporda yalnızca biri görünüyordu", "Bütün ayrık döngüler raporlanıyor"]],
      [0.25, 0.45, 0.3])]),
]

# ============================================================
story += H1("7. Sonuç ve Gelecek Çalışmalar")
story += [
    H2("7.1 Başarı kriterleri"),
    T([["Kriter", "Durum"],
       ["En az bir deadlock senaryosunu doğru tespit etmek", "Sağlandı: tek, çoklu ve çok örnekli kaynaklı senaryolar"],
       ["Deadlock'a dahil process ve kaynakları göstermek", "Sağlandı: durum paneli, kart vurgusu, graf üzerinde döngü"],
       ["Belirlenen koşullarda deadlock risk uyarısı vermek", "Sağlandı: dört risk seviyesi ve nedenleri, Banker's uyarısı"],
       ["En az bir recovery yöntemi uygulamak", "Sağlandı: sonlandırma ve kaynak geri alma"],
       ["Recovery sonrası sistemin güvenli duruma döndüğünü göstermek", "Sağlandı: Banker's güvenli sıra buluyor"],
       ["Normal ve deadlock durumlarını karşılaştırmak", "Sağlandı: normal çalışma senaryosu ve risk seyri"],
       ["Kodun modüler olması", "Sağlandı: katmanlı mimari; algoritmalar arayüzden bağımsız test edildi"],
       ["Baştan sona çalışan bir demo", "Sağlandı: final_demo.json ve web arayüzü"]],
      [0.55, 0.45]),
    H2("7.2 Sınırlamalar"),
] + B([
    "Sistem bir <b>simülasyondur</b>; gerçek işletim sistemi process'lerini ya da kilitlerini izlemez.",
    "Risk seviyeleri bir <b>sezgisel kuraldır</b> (heuristic); %20 eşiği ekip kararıdır, kesin garanti vermez.",
    "Banker's güvensiz isteği yalnızca uyarır, engellemez; Max bildirilmeyen senaryolarda HIGH seviyesi "
    "değerlendirilemez.",
    "Kaynak geri almada rollback basitleştirilmiştir: process yalnızca o kaynağı almadan önceki noktaya döner.",
    "Bekleme kuyruğu karşılanabilen istekleri öne alarak servis eder; büyük istekler geride kalabilir (starvation).",
    "Web arayüzü tek kullanıcılıdır ve yerel demo için tasarlanmıştır.",
]) + [
    H2("7.3 Gelecek çalışmalar"),
] + B([
    "<b>Kaçınma modu:</b> Banker's'ın güvensiz isteği engellediği, ayarlanabilir bir mod.",
    "<b>Gerçek sisteme bağlantı:</b> Bir programdaki kilit (mutex) kullanımını izleyip aynı RAG'e dönüştürmek; "
    "örneğin veritabanlarındaki kilit bekleme grafları (wait-for graph) bu yaklaşımla çalışır.",
    "<b>Önleme stratejileri:</b> Kaynaklara sıra numarası vererek döngüsel beklemeyi imkânsız kılan kaynak "
    "sıralama (resource ordering) yönteminin karşılaştırmalı gösterimi.",
    "<b>Zamanlama:</b> Olayların senaryodan değil, zamanlayıcıyla rastgele üretildiği bir yük testi modu.",
])

# ============================================================
story += H1("8. Kaynakça")
story += B([
    "A. Silberschatz, P. B. Galvin, G. Gagne, <i>Operating System Concepts</i>, 10. baskı, Wiley, 2018. "
    "Bölüm 8: Deadlocks.",
    "E. G. Coffman, M. J. Elphick, A. Shoshani, \"System Deadlocks\", <i>ACM Computing Surveys</i>, 3(2), "
    "s. 67–78, 1971.",
    "R. C. Holt, \"Some Deadlock Properties of Computer Systems\", <i>ACM Computing Surveys</i>, 4(3), "
    "s. 179–196, 1972.",
    "E. W. Dijkstra, \"Cooperating Sequential Processes\", EWD123, Technische Hogeschool Eindhoven, 1965.",
    "Flask belgeleri: flask.palletsprojects.com",
    "pytest ve pytest-cov belgeleri: docs.pytest.org",
])

# ============================================================
story += H1("9. Ekip Katkıları")
story += [
    P("Modüller, proje planında belirlenen dört role göre ayrılmıştır. Sorumlu sütunu ekip tarafından "
      "doldurulacaktır."),
    T([["Rol", "Modüller", "Sorumlu"],
       ["Simülasyon ve veri modeli", "process.py, resource.py, event_log.py, engine.py, scenario_loader.py, "
                                     "scenarios/", ""],
       ["Tespit ve kurtarma", "detection.py, recovery.py", ""],
       ["Risk analizi", "bankers.py, risk.py", ""],
       ["Arayüz ve görselleştirme", "app.py, dashboard_view.py, graph_view.py, html_view.py, run_scenario.py", ""],
       ["Test ve belgeler", "tests/, Test Raporu, bu rapor", ""]],
      [0.26, 0.49, 0.25], min_rows_height=1.3 * cm),
]

if __name__ == "__main__":
    out = str(HERE / "Deadlock_Guardian_Final_Rapor.pdf")
    Doc(out).multiBuild(story)
    print("ok", out)
