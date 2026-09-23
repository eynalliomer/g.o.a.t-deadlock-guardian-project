"""Deadlock Guardian — 11 haftalık el kitabı (bilgi havuzu) PDF'ini üretir."""
from reportlab.graphics.shapes import Circle, Drawing, Line, Polygon, Rect, String
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, Frame, KeepTogether, PageBreak,
                                PageTemplate, Paragraph, Preformatted, Spacer,
                                Table, TableStyle)
from reportlab.platypus.tableofcontents import TableOfContents
import math

FD = "/System/Library/Fonts/Supplemental/"
for name, f in [("A", "Arial.ttf"), ("AB", "Arial Bold.ttf"), ("AI", "Arial Italic.ttf"),
                ("M", "Courier New.ttf")]:
    pdfmetrics.registerFont(TTFont(name, FD + f))
pdfmetrics.registerFontFamily("A", normal="A", bold="AB", italic="AI", boldItalic="AB")

NAVY = colors.HexColor("#1B3A5C")
LINE = colors.HexColor("#B8C4D0")
ZEBRA = colors.HexColor("#F3F6F9")
RED = colors.HexColor("#C0392B")
GREY = colors.HexColor("#555555")
BOX = {  # başlık, çizgi rengi, zemin
    "tanim": ("Tanım", colors.HexColor("#2E6DA4"), colors.HexColor("#EEF4FA")),
    "ornek": ("Örnek", colors.HexColor("#2E8B57"), colors.HexColor("#EEF7F1")),
    "dikkat": ("Dikkat", colors.HexColor("#D68910"), colors.HexColor("#FDF5E8")),
    "proje": ("Projemizde", colors.HexColor("#6C3483"), colors.HexColor("#F5EEF8")),
    "ozet": ("Bu bölümün sonunda bilmeniz gerekenler", NAVY, colors.HexColor("#F3F6F9")),
}

W = A4[0] - 3.6 * cm

st = {
    "cover": ParagraphStyle("cover", fontName="AB", fontSize=30, leading=36, alignment=TA_CENTER, textColor=NAVY),
    "coversub": ParagraphStyle("cs", fontName="A", fontSize=13, leading=19, alignment=TA_CENTER, textColor=GREY),
    "h1": ParagraphStyle("h1", fontName="AB", fontSize=18, leading=23, textColor=NAVY, spaceAfter=4),
    "h1sub": ParagraphStyle("h1s", fontName="A", fontSize=10.5, leading=14, textColor=GREY, spaceAfter=10),
    "h2": ParagraphStyle("h2", fontName="AB", fontSize=13, leading=17, textColor=NAVY, spaceBefore=10, spaceAfter=4, keepWithNext=1),
    "h3": ParagraphStyle("h3", fontName="AB", fontSize=10.8, leading=14, spaceBefore=6, spaceAfter=2, keepWithNext=1),
    "p": ParagraphStyle("p", fontName="A", fontSize=10, leading=14.5, spaceAfter=5),
    "cell": ParagraphStyle("c", fontName="A", fontSize=8.9, leading=11.8),
    "cellh": ParagraphStyle("ch", fontName="AB", fontSize=8.9, leading=11.8, textColor=colors.white),
    "boxt": ParagraphStyle("bt", fontName="AB", fontSize=9.5, leading=12.5),
    "boxp": ParagraphStyle("bp", fontName="A", fontSize=9.6, leading=13.6, spaceAfter=2),
    "bul": ParagraphStyle("bul", fontName="A", fontSize=10, leading=14, leftIndent=12, bulletIndent=2, spaceAfter=2),
    "bbul": ParagraphStyle("bbul", fontName="A", fontSize=9.6, leading=13.4, leftIndent=12, bulletIndent=2, spaceAfter=1),
    "code": ParagraphStyle("code", fontName="M", fontSize=8.6, leading=11),
    "toc0": ParagraphStyle("toc0", fontName="A", fontSize=10.5, leading=17, leftIndent=0),
}


# ---------- yapı taşları ----------
class Chapter(Paragraph):
    """İçindekiler tablosuna kaydolan bölüm başlığı."""


def H1(title, sub=None):
    out = [PageBreak(), Chapter(title, st["h1"])]
    if sub:
        out.append(Paragraph(sub, st["h1sub"]))
    return out


def H2(t): return Paragraph(t, st["h2"])
def H3(t): return Paragraph(t, st["h3"])
def P(t): return Paragraph(t, st["p"])


def B(items, style="bul"):
    return [Paragraph(i, st[style], bulletText="•") for i in items]


def Box(kind, content, title=None):
    label, edge, bg = BOX[kind]
    inner = [Paragraph(title or label, ParagraphStyle("x", parent=st["boxt"], textColor=edge))]
    for c in content if isinstance(content, list) else [content]:
        if isinstance(c, str):
            inner.append(Paragraph(c, st["boxp"]))
        else:
            inner.append(c)
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
    pre = Preformatted(text.strip("\n"), st["code"])
    t = Table([[pre]], colWidths=[W])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F4F4F4")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#DDDDDD")),
        ("LEFTPADDING", (0, 0), (-1, -1), 8), ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    return KeepTogether([t, Spacer(1, 7)])


def T(rows, widths, center_cols=()):
    data = [[Paragraph(str(c), st["cellh"] if i == 0 else st["cell"]) for c in r] for i, r in enumerate(rows)]
    t = Table(data, colWidths=[w * W for w in widths], repeatRows=1)
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("BOX", (0, 0), (-1, -1), 0.6, LINE), ("INNERGRID", (0, 0), (-1, -1), 0.3, LINE),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, ZEBRA]),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5), ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 3.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
    ]
    t.setStyle(TableStyle(style))
    return KeepTogether([t, Spacer(1, 8)])


# ---------- şekiller ----------
def arrow(d, x1, y1, x2, y2, r1=0, r2=0, color=colors.black, width=1.2, label=None, lab_dy=5, lab_dx=0):
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy)
    ux, uy = dx / L, dy / L
    sx, sy = x1 + ux * r1, y1 + uy * r1
    ex, ey = x2 - ux * r2, y2 - uy * r2
    d.add(Line(sx, sy, ex, ey, strokeColor=color, strokeWidth=width))
    s = 7
    px, py = -uy, ux
    d.add(Polygon([ex, ey, ex - ux * s + px * s * 0.45, ey - uy * s + py * s * 0.45,
                   ex - ux * s - px * s * 0.45, ey - uy * s - py * s * 0.45],
                  fillColor=color, strokeColor=color))
    if label:
        d.add(String((sx + ex) / 2 + lab_dx, (sy + ey) / 2 + lab_dy, label, fontName="A", fontSize=7.5,
                     fillColor=GREY, textAnchor="middle"))


def proc(d, x, y, name, r=17, color=NAVY):
    d.add(Circle(x, y, r, fillColor=colors.HexColor("#EEF4FA"), strokeColor=color, strokeWidth=1.4))
    d.add(String(x, y - 3.5, name, fontName="AB", fontSize=10, textAnchor="middle"))


def res(d, x, y, name, n=1, s=34):
    d.add(Rect(x - s / 2, y - s / 2, s, s, fillColor=colors.HexColor("#FDF5E8"),
               strokeColor=colors.HexColor("#B9770E"), strokeWidth=1.4))
    d.add(String(x, y + s / 2 + 4, name, fontName="AB", fontSize=10, textAnchor="middle"))
    gap = 9
    start = x - gap * (n - 1) / 2
    for i in range(n):
        d.add(Circle(start + i * gap, y, 2.6, fillColor=colors.black, strokeColor=colors.black))


def caption(d, text, y=6):
    d.add(String(d.width / 2, y, text, fontName="AI", fontSize=8.5, fillColor=GREY, textAnchor="middle"))


def fig_states():
    d = Drawing(W, 150)
    nodes = {"NEW": (50, 105), "READY": (170, 105), "RUNNING": (310, 105),
             "WAITING": (240, 35), "TERMINATED": (440, 105)}
    for n, (x, y) in nodes.items():
        c = colors.HexColor("#EEF4FA")
        d.add(Rect(x - 42, y - 13, 84, 26, rx=8, ry=8, fillColor=c, strokeColor=NAVY, strokeWidth=1.2))
        d.add(String(x, y - 3.5, n, fontName="AB", fontSize=8.5, textAnchor="middle"))
    arrow(d, 92, 105, 128, 105, label="kabul")
    arrow(d, 212, 112, 268, 112, label="CPU'ya alındı", lab_dy=4)
    arrow(d, 268, 98, 212, 98, label="süresi doldu", lab_dy=-11)
    arrow(d, 352, 105, 398, 105, label="bitti")
    arrow(d, 300, 92, 262, 48, label="kaynak bekliyor", lab_dy=-4, lab_dx=44)
    arrow(d, 222, 48, 185, 92, label="kaynak geldi", lab_dy=-4, lab_dx=-38)
    caption(d, "Şekil 1 — Process durumları ve aralarındaki geçişler (Silberschatz, Bölüm 3)")
    return d


def fig_rag_deadlock():
    d = Drawing(W, 175)
    cx = W / 2
    proc(d, cx - 110, 105, "P1")
    proc(d, cx + 110, 105, "P2")
    res(d, cx, 145, "R1")
    res(d, cx, 55, "R2")
    arrow(d, cx, 145, cx - 110, 105, 20, 17, RED, 1.6, "atanmış")
    arrow(d, cx - 110, 105, cx, 55, 17, 20, RED, 1.6, "istiyor", -12)
    arrow(d, cx, 55, cx + 110, 105, 20, 17, RED, 1.6, "atanmış", -12)
    arrow(d, cx + 110, 105, cx, 145, 17, 20, RED, 1.6, "istiyor")
    caption(d, "Şekil 2 — Deadlock: P1 → R2 → P2 → R1 → P1 döngüsü (her kaynaktan 1 adet var)")
    return d


def fig_rag_nodeadlock():
    d = Drawing(W, 185)
    cx = W / 2
    proc(d, cx - 140, 110, "P1")
    proc(d, cx + 40, 110, "P2")
    proc(d, cx + 180, 150, "P3")
    res(d, cx - 50, 155, "R1", n=2)
    res(d, cx - 50, 55, "R2", n=1)
    arrow(d, cx - 140, 110, cx - 50, 155, 17, 20, RED, 1.5, "istiyor")
    arrow(d, cx - 50, 155, cx + 40, 110, 20, 17, RED, 1.5, "atanmış")
    arrow(d, cx - 50, 155, cx + 180, 150, 20, 17, colors.HexColor("#2E8B57"), 1.5, "atanmış")
    arrow(d, cx + 40, 110, cx - 50, 55, 17, 20, RED, 1.5, "istiyor", -12)
    arrow(d, cx - 50, 55, cx - 140, 110, 20, 17, RED, 1.5, "atanmış", -12)
    d.add(String(cx + 180, 122, "kimseyi beklemiyor", fontName="A", fontSize=7.5,
                 fillColor=colors.HexColor("#2E8B57"), textAnchor="middle"))
    caption(d, "Şekil 3 — Döngü var ama deadlock yok: R1'in 2 adedi var, P3 bitince bir adet boşalır")
    return d


def fig_waitfor():
    d = Drawing(W, 95)
    cx = W / 2
    proc(d, cx - 70, 50, "P1")
    proc(d, cx + 70, 50, "P2")
    arrow(d, cx - 70, 58, cx + 70, 58, 17, 17, RED, 1.5, "P2'yi bekliyor")
    arrow(d, cx + 70, 42, cx - 70, 42, 17, 17, RED, 1.5, "P1'i bekliyor", -12)
    caption(d, "Şekil 4 — Şekil 2'nin wait-for graph hali: kaynak düğümleri kaldırılır", 2)
    return d


def fig_arch():
    d = Drawing(W, 200)
    def box(x, y, w, h, text, sub, color):
        d.add(Rect(x, y, w, h, rx=6, ry=6, fillColor=color, strokeColor=NAVY, strokeWidth=1))
        d.add(String(x + w / 2, y + h / 2 + 2, text, fontName="AB", fontSize=9, textAnchor="middle"))
        d.add(String(x + w / 2, y + h / 2 - 10, sub, fontName="A", fontSize=7.5, fillColor=GREY, textAnchor="middle"))
    light = colors.HexColor("#EEF4FA")
    box(20, 160, W - 40, 32, "Arayüz (Hafta 5 ve 9)", "dashboard, graf, uyarılar, butonlar", colors.HexColor("#F5EEF8"))
    box(20, 108, W - 40, 32, "Simülasyon Motoru (Hafta 2-3)", "Process, Resource, request / release, olay kaydı", light)
    third = (W - 40 - 20) / 3
    box(20, 52, third, 36, "Tespit", "Hafta 4 — RAG, DFS", colors.HexColor("#FDEDEC"))
    box(30 + third, 52, third, 36, "Risk Analizi", "Hafta 6-7 — Banker's", colors.HexColor("#FDF5E8"))
    box(40 + 2 * third, 52, third, 36, "Recovery", "Hafta 8 — kurban seçimi", colors.HexColor("#EEF7F1"))
    box(20, 12, W - 40, 26, "Veri (JSON senaryolar, log)", "", light)
    for x in (W / 2,):
        arrow(d, x, 160, x, 140)
        arrow(d, x, 108, x, 88)
    arrow(d, 20 + third / 2, 108, 20 + third / 2, 88)
    arrow(d, 40 + 2.5 * third, 108, 40 + 2.5 * third, 88)
    arrow(d, W / 2, 52, W / 2, 38)
    return d


# ---------- belge şablonu ----------
class Doc(BaseDocTemplate):
    def __init__(self, path):
        super().__init__(path, pagesize=A4, leftMargin=1.8 * cm, rightMargin=1.8 * cm,
                         topMargin=1.7 * cm, bottomMargin=1.7 * cm,
                         title="Deadlock Guardian — El Kitabı", author="Deadlock Guardian Ekibi")
        frame = Frame(self.leftMargin, self.bottomMargin, self.width, self.height, id="f")
        self.addPageTemplates([PageTemplate(id="p", frames=[frame], onPage=self.footer)])

    def footer(self, c, doc):
        if doc.page == 1:
            return
        c.saveState()
        c.setFont("A", 8)
        c.setFillColor(colors.HexColor("#777777"))
        c.drawString(1.8 * cm, 1 * cm, "Deadlock Guardian — 11 Haftalık El Kitabı")
        c.drawRightString(A4[0] - 1.8 * cm, 1 * cm, f"Sayfa {doc.page}")
        c.restoreState()

    def afterFlowable(self, f):
        if isinstance(f, Chapter):
            self.notify("TOCEntry", (0, f.getPlainText(), self.page))


# ============================================================
story = []

# --- Kapak ---
story += [Spacer(1, 5 * cm), Paragraph("DEADLOCK GUARDIAN", st["cover"]), Spacer(1, 10),
          Paragraph("11 Haftalık El Kitabı ve Bilgi Havuzu", ParagraphStyle(
              "c2", parent=st["coversub"], fontName="AB", fontSize=15, textColor=colors.black)),
          Spacer(1, 14),
          Paragraph("Projeyi yaparken karşılaşacağımız tüm kavramlar, tanımlar,<br/>"
                    "açıklamalar ve örnekler — hafta hafta", st["coversub"]),
          Spacer(1, 4 * cm),
          Paragraph("İşletim Sistemleri Dersi · Yazılım Mühendisliği Bölümü<br/>"
                    "Ana kaynak: Silberschatz, Galvin, Gagne — <i>Operating System Concepts</i>, 10. baskı",
                    st["coversub"])]

# --- İçindekiler ---
toc = TableOfContents()
toc.levelStyles = [st["toc0"]]
toc.dotsMinLevel = 0
story += [PageBreak(), Paragraph("İçindekiler", st["h1"]), Spacer(1, 6), toc]

# ============================================================
story += H1("0. Başlamadan Önce", "Bu kitap nasıl kullanılır, proje nedir, bölümümüzle ne ilgisi var")
story += [
    H2("Bu kitap nasıl kullanılır?"),
    P("Her bölüm, 11 haftalık plandaki bir haftaya karşılık gelir. O haftaya başlamadan önce ilgili bölümü "
      "okuyun. Her bölümde aynı kutu türlerini göreceksiniz:"),
    T([["Kutu", "Ne anlatır?"],
       ["<b>Tanım</b>", "Terimin kısa ve kesin anlamı. Sınavda ve raporda kullanılabilecek cümle."],
       ["<b>Örnek</b>", "Kavramı somutlaştıran gündelik hayat ya da sayısal örnek."],
       ["<b>Dikkat</b>", "Sık yapılan hatalar ve karıştırılan kavramlar."],
       ["<b>Projemizde</b>", "Kavramın Deadlock Guardian'da tam olarak nereye karşılık geldiği."],
       ["<b>Bilmeniz gerekenler</b>", "Bölüm sonu kontrol listesi. Hepsini açıklayabiliyorsanız o haftaya hazırsınız."]],
      [0.25, 0.75]),
    P("Terimler kitapta İngilizce karşılıklarıyla birlikte verilmiştir; çünkü hem ders kitabı hem de kod "
      "İngilizcedir. Kitabın sonunda Türkçe-İngilizce bir sözlük vardır (Ek C)."),

    H2("Proje tek paragrafta"),
    P("Bilgisayarda aynı anda birçok program (process) çalışır ve bu programlar dosya, yazıcı, kilit gibi "
      "kaynakları paylaşır. Bazen iki program birbirinin elindeki kaynağı bekler ve ikisi de sonsuza kadar "
      "takılı kalır: buna <b>deadlock</b> denir. <b>Deadlock Guardian</b>, bu durumu kontrollü bir "
      "simülasyon ortamında canlandıran bir yazılımdır. Deadlock olmadan önce riski ölçer ve uyarır "
      "(<b>risk analizi</b>), olduğunda bulur (<b>tespit</b>) ve sistemi tekrar çalışır hale getirir "
      "(<b>recovery</b>)."),
    fig_arch(),
    Paragraph("Şekil 0 — Deadlock Guardian'ın katmanları ve hangi haftada yapıldıkları",
              ParagraphStyle("cap", parent=st["p"], fontName="AI", fontSize=8.5, textColor=GREY,
                             alignment=TA_CENTER)),

    H2("Bu proje ve Yazılım Mühendisliği bölümümüz"),
    P("İşletim Sistemleri dersi, bir yazılımın altında çalışan katmanı öğretir. Yazılım Mühendisliği ise "
      "bir yazılımın <b>planlı, ekipçe, test edilerek ve belgelenerek</b> nasıl üretileceğini öğretir. "
      "Bu proje ikisini birleştirir: konu işletim sistemlerinden, yapılış biçimi yazılım mühendisliğinden "
      "gelir. Hoca projeyi değerlendirirken yalnızca algoritmanın doğruluğuna değil, projenin nasıl "
      "yönetildiğine de bakacaktır."),
    T([["Yazılım Mühendisliği kavramı", "Bu projede nerede karşımıza çıkıyor?"],
       ["Yazılım geliştirme yaşam döngüsü (SDLC)", "Plan → tasarım → kodlama → test → teslim. 11 haftalık plan bu döngünün ta kendisi."],
       ["Artımlı (incremental) geliştirme", "Her hafta çalışan sisteme yeni bir parça eklenir; 2. haftanın simülasyonu 4. haftada tespitle, 8. haftada recovery ile büyür."],
       ["Gereksinim analizi", "Sistemin ne yapması gerektiğinin yazılması (Ek A'da örnekler var)."],
       ["Modüler tasarım", "Simülasyon, tespit, risk, recovery ve arayüz ayrı modüller; 4 kişi aynı anda çalışabilir."],
       ["Nesne yönelimli programlama (OOP)", "Process ve Resource birer sınıf (class) olarak yazılır."],
       ["Sürüm kontrolü (Git)", "Dört kişinin kodu GitHub'da birleştirilir; kim neyi ne zaman değiştirdi görülür."],
       ["Yazılım testi", "10. hafta ve her modülün kendi birim testleri."],
       ["Dokümantasyon", "Bu el kitabı, Obsidian notları, README ve final raporu."]],
      [0.36, 0.64]),
    Box("proje", "Hafta 1'in görev dağılımı: <b>Üye 1</b> simülasyon ve veri modeli, <b>Üye 2</b> tespit ve "
        "recovery, <b>Üye 3</b> risk analizi, <b>Üye 4</b> arayüz ve görselleştirme. Herkes kendi "
        "haftalarının bölümünü derinlemesine, diğer bölümleri ise en az bir kez okumalıdır."),
]

# ============================================================
story += H1("1. Hafta — Temel Kavramlar ve Deadlock", "Konuyu anlama ve proje tasarımı")
story += [
    H2("1.1 İşletim sistemi nedir?"),
    Box("tanim", "<b>İşletim sistemi (operating system)</b>, donanım ile kullanıcı programları arasında "
        "duran ve bilgisayarın kaynaklarını (işlemci, bellek, disk, cihazlar) programlar arasında "
        "paylaştıran yazılımdır. Ders kitabı onu bir <b>kaynak dağıtıcı (resource allocator)</b> olarak tanımlar."),
    P("Kaynak dağıtıcı olmanın zor kısmı, kaynakların sınırlı, isteyenlerin ise çok olmasıdır. İşletim sistemi "
      "\"kime, neyi, ne zaman vereceğine\" karar verir. Deadlock da tam bu kararların yanlış bir sıraya "
      "girmesiyle ortaya çıkar."),

    H2("1.2 Program ve process"),
    Box("tanim", ["<b>Program:</b> diskte duran, çalışmayan komutlar dosyası (ör. <i>chrome.exe</i>). Pasiftir.",
                  "<b>Process (süreç):</b> çalışmakta olan program. Aktiftir; belleği, durumu ve kullandığı kaynakları vardır. "
                  "Aynı programı iki kez açarsanız iki ayrı process oluşur."]),
    P("İşletim sistemi her process için bir <b>Process Control Block (PCB)</b> tutar: process'in kimliği (PID), "
      "durumu, önceliği ve elindeki kaynaklar bu kayıtta durur. Bizim yazacağımız <i>Process</i> sınıfı, "
      "PCB'nin küçük bir benzeridir."),
    H3("Process durumları"),
    fig_states(),
    T([["Durum", "Anlamı"],
       ["NEW", "Process oluşturuluyor."],
       ["READY", "Çalışmaya hazır, işlemci sırası bekliyor."],
       ["RUNNING", "Şu anda işlemcide çalışıyor."],
       ["WAITING", "Bir olayı ya da kaynağı bekliyor; o gelmeden ilerleyemez."],
       ["TERMINATED", "Çalışması bitti."]], [0.22, 0.78]),
    Box("proje", "Simülasyonumuzda işlemci zamanlamasıyla uğraşmadığımız için durumları sadeleştiriyoruz: "
        "<b>RUNNING</b> (ilerleyebiliyor), <b>WAITING</b> (bir kaynağı bekliyor) ve <b>TERMINATED</b> "
        "(bitti ya da recovery ile sonlandırıldı). Deadlock'taki process'ler hep WAITING durumundadır."),
    Box("dikkat", "<b>Thread</b> ile process karıştırılmamalı. Thread, bir process'in içindeki çalışma "
        "akışıdır; aynı process'in thread'leri belleği paylaşır. Deadlock thread'ler arasında da olur "
        "(iki thread iki kilidi ters sırayla almaya çalışırsa). Projemizde \"process\" diyoruz ama "
        "anlattığımız her şey thread'ler için de geçerlidir."),

    H2("1.3 Kaynak (resource)"),
    Box("tanim", "<b>Kaynak</b>, bir process'in işini yapabilmek için ihtiyaç duyduğu ve sayısı sınırlı olan "
        "her şeydir: yazıcı, dosya, veritabanı kaydı, bellek bölgesi, kilit (mutex), ağ bağlantısı..."),
    T([["Kavram", "Açıklama", "Örnek"],
       ["Kaynak tipi (resource type)", "Aynı türden kaynakların grubu", "Yazıcılar = R1"],
       ["Örnek / adet (instance)", "Bir kaynak tipinin kaç tane birbirinin aynısı kopyası olduğu", "Laboratuvarda 3 yazıcı → R1'in 3 örneği var"],
       ["Tek örnekli kaynak", "Tipten yalnızca bir tane var", "Tek bir dosya kilidi"],
       ["Çok örnekli kaynak", "Tipten birden fazla var; hangisinin verildiği önemsiz", "3 yazıcıdan herhangi biri"],
       ["Paylaşılamaz (non-sharable)", "Aynı anda yalnızca bir process kullanabilir", "Yazıcı, yazma kilidi"],
       ["Geri alınamaz (non-preemptable)", "Process bırakmadan elinden zorla alınamaz", "Yarıda kesilemeyen yazdırma işi"]],
      [0.27, 0.43, 0.30]),
    H3("Kaynak kullanım döngüsü"),
    P("Bir process bir kaynağı her zaman aynı üç adımla kullanır:"),
] + B(["<b>Request (iste):</b> kaynak boşsa hemen alınır; doluysa process bekler (WAITING).",
       "<b>Use (kullan):</b> process kaynakla işini yapar.",
       "<b>Release (bırak):</b> process kaynağı serbest bırakır; bekleyen varsa ona verilir."]) + [
    Box("proje", "2. haftada yazacağımız <i>request()</i> ve <i>release()</i> fonksiyonları bu döngünün koda "
        "dökülmüş halidir. \"Use\" adımını simülasyonda atlarız; kaynağı elinde tutmak kullanıyor sayılır."),

    H2("1.4 Deadlock nedir?"),
    Box("tanim", "<b>Deadlock (kilitlenme)</b>: bir grup process'in her birinin, yine o gruptaki başka bir "
        "process'in elindeki kaynağı beklemesi ve bu yüzden hiçbirinin ilerleyememesi durumudur. "
        "Dışarıdan bir müdahale olmadan bu bekleme sonsuza kadar sürer."),
    Box("ornek", ["<b>Gündelik hayat:</b> Dar bir köprüye iki yönden aynı anda iki araba girer. İkisi de "
                  "karşıdakinin geri çekilmesini bekler; kimse geri çekilmezse ikisi de orada kalır.",
                  "<b>Bilgisayarda:</b> P1 dosyayı açıp kilitledi, şimdi yazıcıyı istiyor. P2 yazıcıyı almış, "
                  "şimdi dosyayı istiyor. P1, P2'nin yazıcıyı bırakmasını; P2, P1'in dosyayı bırakmasını "
                  "bekler. Hiçbiri kendi elindekini bırakmaz."]),
    T([["Process", "Elindeki kaynak", "Beklediği kaynak"],
       ["P1", "R1 (dosya)", "R2 (yazıcı)"],
       ["P2", "R2 (yazıcı)", "R1 (dosya)"]], [0.2, 0.4, 0.4]),

    H2("1.5 Deadlock'un dört koşulu (Coffman koşulları)"),
    P("Deadlock ancak aşağıdaki <b>dört koşulun dördü birden</b> aynı anda sağlanırsa oluşabilir. "
      "Biri bile eksikse deadlock olmaz. Bu, konunun en önemli bilgisidir."),
    T([["Koşul", "Anlamı", "Yukarıdaki örnekte"],
       ["1. Mutual exclusion (karşılıklı dışlama)", "Kaynak aynı anda yalnızca bir process tarafından kullanılabilir.", "Yazıcıyı iki process aynı anda kullanamaz."],
       ["2. Hold and wait (tut ve bekle)", "Process elindeki kaynağı bırakmadan başka bir kaynak bekler.", "P1 dosyayı tutarken yazıcıyı bekliyor."],
       ["3. No preemption (geri alınamazlık)", "Kaynak, sahibinden zorla alınamaz; sahibi kendisi bırakmalıdır.", "Kimse P2'nin elinden yazıcıyı alamıyor."],
       ["4. Circular wait (döngüsel bekleme)", "P1 → P2 → ... → Pn → P1 şeklinde kapalı bir bekleme zinciri vardır.", "P1, P2'yi; P2, P1'i bekliyor."]],
      [0.3, 0.4, 0.3]),
    Box("dikkat", "Dört koşul <b>gerekli</b> koşullardır, yani deadlock varsa dördü de mutlaka vardır. "
        "Ama çok örnekli kaynaklarda dördü birden olsa bile deadlock olmayabilir (Bölüm 4'te göreceğiz). "
        "Tek örnekli kaynaklarda ise döngüsel bekleme = deadlock'tur."),

    H2("1.6 Deadlock ile karıştırılan kavramlar"),
    T([["Kavram", "Ne oluyor?", "Deadlock'tan farkı"],
       ["Starvation (açlık)", "Bir process kaynağı hiç alamaz, çünkü sıra hep başkalarına gelir.", "Sistem ilerliyor; sadece bir process sürekli geride kalıyor."],
       ["Livelock", "Process'ler sürekli durum değiştirir ama hiçbiri işini bitiremez (koridorda sürekli aynı tarafa kaçan iki kişi).", "Process'ler WAITING değil, aktif; ama yine de ilerleme yok."],
       ["Yavaşlık", "Kaynak dolu olduğu için bir süre beklenir, sonra alınır.", "Bekleme sonludur; deadlock'ta sonsuzdur."]],
      [0.2, 0.45, 0.35]),

    H2("1.7 Deadlock ile başa çıkmanın dört yolu"),
    T([["Yöntem", "Fikir", "Projemizde"],
       ["Prevention (önleme)", "Dört koşuldan birini tamamen imkânsız kılmak. En pratiği: kaynakları hep aynı sırayla istemek (döngüsel beklemeyi kırar).", "Recovery önerilerinde \"kaynak sırasını düzelt\" tavsiyesi olarak."],
       ["Avoidance (kaçınma)", "Her isteği vermeden önce \"bu sistemi tehlikeye sokar mı?\" diye hesaplamak. Banker's Algorithm.", "Hafta 6-7: Risk analizi"],
       ["Detection + Recovery (tespit ve kurtarma)", "Deadlock olmasına izin vermek, sonra bulup çözmek.", "Hafta 4 ve Hafta 8"],
       ["Ignore (görmezden gelme)", "Deadlock'un nadir olduğunu varsayıp hiçbir şey yapmamak. Linux ve Windows dahil çoğu işletim sistemi bunu yapar; sorunu uygulama geliştiricisine bırakır.", "Bu yüzden projemiz gibi araçlar anlamlıdır."]],
      [0.24, 0.46, 0.30]),
    Box("proje", "Deadlock Guardian, ders kitabındaki yöntemlerden üçünü tek sistemde birleştirir: "
        "<b>avoidance</b> (risk analizi), <b>detection</b> (tespit) ve <b>recovery</b> (kurtarma). "
        "Projeyi özgün yapan da budur."),
    Box("ozet", B(["İşletim sisteminin neden bir kaynak dağıtıcı olduğunu",
                   "Program ile process arasındaki farkı, process durumlarını",
                   "Kaynak tipi ile kaynak örneği (instance) farkını; request → use → release döngüsünü",
                   "Deadlock'un tanımını ve bir örnekle anlatmayı",
                   "Dört Coffman koşulunu ezbere ve örnekleriyle",
                   "Deadlock, starvation ve livelock farkını",
                   "Dört başa çıkma yöntemini ve projemizin hangilerini kullandığını"], "bbul")),
]

# ============================================================
story += H1("2. Hafta — Basit Simülasyon", "Process ve kaynakları koda dökmek")
story += [
    H2("2.1 Simülasyon nedir, neden gerçek process kullanmıyoruz?"),
    Box("tanim", "<b>Simülasyon</b>, gerçek bir sistemin davranışını yazılım içinde taklit eden modeldir. "
        "Bizim simülasyonumuzda \"P1\" gerçek bir program değil, bilgisayarın belleğinde duran bir nesnedir."),
    P("Gerçek işletim sistemindeki process'leri kilitlemek hem tehlikeli (bilgisayar donabilir) hem de "
      "kontrolsüzdür (deadlock'u istediğimiz anda oluşturamayız). Simülasyonda ise senaryoyu biz yazarız: "
      "\"P1 R1'i alsın, P2 R2'yi alsın, sonra çapraz istesinler\" deriz ve deadlock tam istediğimiz anda oluşur. "
      "Bu karar proje belgesinde de yazılıdır: ilk sürüm kontrollü bir simülasyondur."),

    H2("2.2 Sınıf ve nesne (OOP)"),
    Box("tanim", ["<b>Sınıf (class):</b> bir şeyin kalıbı. \"Her process'in bir kimliği ve durumu vardır\" der.",
                  "<b>Nesne (object):</b> kalıptan üretilmiş somut örnek. P1 ve P2, Process sınıfının iki nesnesidir.",
                  "<b>Özellik (attribute):</b> nesnenin taşıdığı veri (pid, state).",
                  "<b>Metot (method):</b> nesnenin yapabildiği iş (request, release)."]),
    P("Projede iki temel sınıfımız olacak:"),
    T([["Sınıf", "Özellikler", "Ne işe yarar?"],
       ["Process", "pid (kimlik), state (durum), held (tuttuğu kaynaklar)", "Bir çalışan programı temsil eder."],
       ["Resource", "rid (kimlik), owner (sahibi), queue (bekleyenler)", "Bir kaynağı temsil eder."]],
      [0.16, 0.46, 0.38]),

    H2("2.3 Durum makinesi (state machine)"),
    P("Process'in durumu rastgele değişmez; yalnızca belirli olaylarla belirli yönlere geçer. Buna "
      "<b>durum makinesi</b> denir. Kurallarımız:"),
    T([["Şu anki durum", "Olay", "Yeni durum"],
       ["RUNNING", "Boş bir kaynağı istedi", "RUNNING (kaynak verildi)"],
       ["RUNNING", "Dolu bir kaynağı istedi", "WAITING (kuyruğa girdi)"],
       ["WAITING", "Beklediği kaynak kendisine verildi", "RUNNING"],
       ["RUNNING / WAITING", "Sonlandırıldı", "TERMINATED (tuttuğu her şey bırakılır)"]],
      [0.28, 0.42, 0.30]),

    H2("2.4 Kuyruk (queue) ve FIFO"),
    Box("tanim", "<b>Kuyruk</b>, elemanların sona eklenip baştan çıkarıldığı veri yapısıdır. "
        "<b>FIFO</b> (First In, First Out): ilk gelen ilk çıkar, tıpkı banka sırası gibi."),
    P("Bir kaynak doluyken onu isteyen process'ler o kaynağın kuyruğuna girer. Kaynak bırakıldığında "
      "kuyruğun başındaki process kaynağı alır. Python'da bunun için <i>collections.deque</i> kullanılır: "
      "<i>append()</i> sona ekler, <i>popleft()</i> baştan çıkarır."),
    Box("dikkat", "FIFO adildir ama deadlock'u engellemez. Kuyruk sırası ne olursa olsun, çapraz bekleme "
        "varsa deadlock olur."),

    H2("2.5 Örnek akış"),
    T([["Adım", "Olay", "Sonuç", "R1'in durumu"],
       ["1", "P1, R1'i istiyor", "R1 boş → P1'e verildi", "sahibi: P1, kuyruk: boş"],
       ["2", "P2, R1'i istiyor", "R1 dolu → P2 WAITING", "sahibi: P1, kuyruk: [P2]"],
       ["3", "P1, R1'i bırakıyor", "Kuyruğun başı P2 → R1 P2'ye verildi, P2 RUNNING", "sahibi: P2, kuyruk: boş"]],
      [0.08, 0.24, 0.40, 0.28]),

    H2("2.6 Kod iskeleti"),
    P("Aşağıdaki kod 2. haftanın hedefinin en küçük çalışan halidir. Birlikte yazarken bunu adım adım "
      "genişleteceğiz; şimdilik mantığı okumanız yeterli."),
    Code('''
from collections import deque
from enum import Enum

class State(Enum):
    RUNNING = "RUNNING"
    WAITING = "WAITING"
    TERMINATED = "TERMINATED"

class Process:
    def __init__(self, pid):
        self.pid = pid                 # "P1" gibi kimlik
        self.state = State.RUNNING
        self.held = []                 # tuttuğu kaynaklar

class Resource:
    def __init__(self, rid):
        self.rid = rid                 # "R1" gibi kimlik
        self.owner = None              # kaynağı tutan process (yoksa None)
        self.queue = deque()           # bekleyen process'ler (FIFO)

def request(p, r):
    if r.owner is None:                # kaynak boş → ver
        r.owner = p
        p.held.append(r)
        p.state = State.RUNNING
    else:                              # kaynak dolu → beklet
        p.state = State.WAITING
        r.queue.append(p)

def release(p, r):
    p.held.remove(r)
    r.owner = None
    if r.queue:                        # bekleyen varsa sıradakine ver
        request(r.queue.popleft(), r)
'''),
    Box("ozet", B(["Neden gerçek process yerine simülasyon kullandığımızı",
                   "Sınıf, nesne, özellik ve metot kavramlarını",
                   "Process durum geçişlerini (durum makinesi)",
                   "Kuyruk ve FIFO mantığını",
                   "request ve release fonksiyonlarının adım adım ne yaptığını"], "bbul")),
]

# ============================================================
story += H1("3. Hafta — Kaynak İlişkileri ve Veri Yapıları", "Sistemin tam fotoğrafını tutmak")
story += [
    H2("3.1 Neden tablolara ihtiyacımız var?"),
    P("2. haftada her kaynak yalnızca \"sahibim kim?\" bilgisini tutuyordu. Ama tespit ve risk analizi "
      "algoritmaları sistemin <b>tamamına</b> bir bakışta bakmak ister: kim neyi tutuyor, kim neyi istiyor, "
      "ne kadar boş kaynak kaldı? Ders kitabı bunun için üç standart yapı kullanır. Bu isimler 4. ve 6. "
      "haftada algoritmaların içinde aynen geçecek."),
    T([["Yapı", "Tür", "Anlamı"],
       ["Available", "Vektör (her kaynak tipi için bir sayı)", "Şu an boşta kaç adet kaynak var?"],
       ["Allocation", "Matris (satır = process, sütun = kaynak tipi)", "Her process her kaynaktan kaç adet tutuyor?"],
       ["Request", "Matris", "Her process her kaynaktan şu an kaç adet daha istiyor (bekliyor)?"],
       ["Max <i>(Hafta 6)</i>", "Matris", "Her process her kaynaktan en fazla kaç adete ihtiyaç duyacağını önceden bildirir."],
       ["Need <i>(Hafta 6)</i>", "Matris", "Need = Max − Allocation: daha ne kadar isteyebilir?"]],
      [0.18, 0.37, 0.45]),
    Box("tanim", ["<b>Vektör:</b> tek satırlık sayı listesi. [3, 2] → R1'den 3, R2'den 2.",
                  "<b>Matris:</b> satır ve sütunlardan oluşan sayı tablosu."]),

    H2("3.2 Çok örnekli kaynaklar: sayısal örnek"),
    P("Sistemde iki kaynak tipi olsun: R1 = yazıcı (toplam 3 adet), R2 = tarayıcı (toplam 2 adet)."),
    T([["Process", "Allocation (R1, R2)", "Request (R1, R2)", "Açıklama"],
       ["P1", "1, 0", "0, 0", "1 yazıcı tutuyor, bir şey beklemiyor"],
       ["P2", "1, 1", "1, 0", "1 yazıcı + 1 tarayıcı tutuyor, 1 yazıcı daha istiyor"],
       ["P3", "1, 1", "0, 1", "1 yazıcı + 1 tarayıcı tutuyor, 1 tarayıcı daha istiyor"]],
      [0.14, 0.22, 0.22, 0.42]),
    P("Toplam tahsis edilen: R1 için 1+1+1 = 3, R2 için 0+1+1 = 2. Demek ki <b>Available = [0, 0]</b>; "
      "boşta hiç kaynak yok. Kural her zaman şudur:"),
    Code("Available = Toplam − (tüm process'lerin Allocation satırlarının toplamı)"),
    Box("dikkat", "Tablolar her request ve release'den sonra tutarlı güncellenmelidir. Bir tablodaki hata, "
        "tespit algoritmasının yanlış sonuç vermesine yol açar. Bu yüzden 3. haftada her işlemden sonra "
        "\"toplamlar tutuyor mu?\" kontrolü yazmak iyi bir fikirdir."),

    H2("3.3 Olay kaydı (log)"),
    Box("tanim", "<b>Log</b>, sistemde olan her olayın zaman sırasıyla yazıldığı kayıttır."),
    Code('''
[0001] P1 REQUEST R1 -> GRANTED
[0002] P2 REQUEST R1 -> WAITING (sahibi P1)
[0003] P1 RELEASE R1 -> R1 P2'ye verildi
'''),
    P("Log, hata ayıklarken \"ne oldu da buraya geldik?\" sorusunun cevabıdır. Arayüzde olay akışı olarak da "
      "gösterilecek. Zaman damgası olarak gerçek saat yerine adım numarası (tick) kullanmak, testleri "
      "tekrar edilebilir yapar."),

    H2("3.4 JSON ile senaryo dosyası"),
    Box("tanim", "<b>JSON</b>, verileri anahtar-değer çiftleriyle yazan, hem insanın hem programın kolayca "
        "okuyabildiği bir metin formatıdır. Python'da <i>json.load()</i> ile tek satırda okunur."),
    Code('''
{
  "resources": {"R1": 1, "R2": 1},
  "processes": ["P1", "P2"],
  "steps": [
    ["P1", "request", "R1"],
    ["P2", "request", "R2"],
    ["P1", "request", "R2"],
    ["P2", "request", "R1"]
  ]
}
'''),
    P("Bu dosya çalıştırıldığında son iki adımda deadlock oluşur. Test ve demo senaryolarını böyle dosyalarda "
      "tutmak, kodu değiştirmeden farklı durumları denemeyi sağlar."),
    Box("proje", "10. haftadaki dört test senaryosu (normal, tek deadlock, çoklu deadlock, recovery) ve final "
        "demosu birer JSON dosyası olacak."),
    Box("ozet", B(["Available, Allocation ve Request yapılarının anlamını",
                   "Available'ın nasıl hesaplandığını",
                   "Çok örnekli kaynak tablosunu okuyup yorumlamayı",
                   "Log'un ve senaryo dosyasının neden gerekli olduğunu, JSON formatını"], "bbul")),
]

# ============================================================
story += H1("4. Hafta — Deadlock Tespiti (Detection)", "Oluşan deadlock'u otomatik bulmak")
story += [
    H2("4.1 Graf nedir?"),
    Box("tanim", ["<b>Graf (graph):</b> düğümlerden ve onları bağlayan kenarlardan oluşan yapı.",
                  "<b>Düğüm (node / vertex):</b> bir nesne; bizde process ya da kaynak.",
                  "<b>Kenar (edge):</b> iki düğüm arasındaki ilişki.",
                  "<b>Yönlü graf (directed graph):</b> kenarların oklu olduğu, yönün önemli olduğu graf.",
                  "<b>Döngü (cycle):</b> bir düğümden çıkıp okları takip ederek aynı düğüme geri dönebilmek."]),

    H2("4.2 Resource Allocation Graph (RAG)"),
    P("Sistemin durumunu gösteren yönlü graftır. Process'ler <b>daire</b>, kaynaklar <b>kare</b> ile çizilir; "
      "karenin içindeki her nokta bir örnektir (instance)."),
    T([["Kenar", "Yön", "Anlamı"],
       ["Request edge (istek kenarı)", "Process → Kaynak", "Process bu kaynağı istiyor ve bekliyor."],
       ["Assignment edge (atama kenarı)", "Kaynak → Process", "Kaynağın bir örneği bu process'e verilmiş."]],
      [0.32, 0.22, 0.46]),
    fig_rag_deadlock(),
    P("Şekil 2'de okları takip edin: P1'den R2'ye, R2'den P2'ye, P2'den R1'e, R1'den tekrar P1'e. "
      "Başladığımız yere döndük: <b>döngü var</b>. Kaynaklar tek örnekli olduğu için bu kesin bir deadlock'tur."),
    fig_rag_nodeadlock(),
    P("Şekil 3'te de P1 → R1 → P2 → R2 → P1 döngüsü var. Ama R1'in <b>iki</b> örneği var ve biri P3'te. "
      "P3 kimseyi beklemediği için işini bitirip R1'i bırakacak. O örnek P1'e verilecek, P1 bitince R2 "
      "boşalacak ve P2 de devam edecek. <b>Döngü var ama deadlock yok.</b>"),
    Box("dikkat", ["<b>Altın kural:</b>",
                   "• Graf'ta döngü yoksa → kesinlikle deadlock yok.",
                   "• Döngü var ve tüm kaynaklar tek örnekliyse → kesinlikle deadlock var.",
                   "• Döngü var ama kaynaklar çok örnekliyse → deadlock <b>olabilir de olmayabilir de</b>; "
                   "aşağıdaki detection algoritması ile kontrol etmek gerekir."]),

    H2("4.3 Wait-for graph"),
    P("Tek örnekli kaynaklarda graf sadeleştirilebilir: kaynak düğümleri silinir, \"P1, R2'yi bekliyor ve "
      "R2'nin sahibi P2\" bilgisi doğrudan <b>P1 → P2</b> (P1, P2'yi bekliyor) okuna dönüşür."),
    fig_waitfor(),

    H2("4.4 DFS ile döngü bulma"),
    Box("tanim", "<b>DFS (Depth-First Search, derinlik öncelikli arama)</b>: bir düğümden başlayıp bir yol "
        "boyunca gidebildiği kadar derine giden, çıkmaz sokağa girince geri dönüp başka yolu deneyen "
        "graf gezme algoritmasıdır."),
    P("Döngü bulmak için düğümleri üç renkle işaretleriz:"),
    T([["Renk", "Anlamı"],
       ["Beyaz", "Henüz hiç ziyaret edilmedi."],
       ["Gri", "Şu an üzerinde yürüdüğümüz yolda (henüz işi bitmedi)."],
       ["Siyah", "Tamamen incelendi; buradan döngüye çıkılmıyor."]], [0.18, 0.82]),
    P("Yürürken <b>gri</b> bir düğüme tekrar ulaşırsak, kendi yolumuzun bir önceki noktasına geri "
      "dönmüşüz demektir: döngü bulundu."),
    Code('''
def has_cycle(graph):
    """graph: {"P1": ["R2"], "R2": ["P2"], ...}  (her düğüm anahtar olmalı)"""
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {node: WHITE for node in graph}

    def dfs(u):
        color[u] = GRAY
        for v in graph[u]:
            if color[v] == GRAY:              # yolumuzdaki düğüme döndük → döngü
                return True
            if color[v] == WHITE and dfs(v):
                return True
        color[u] = BLACK
        return False

    return any(color[n] == WHITE and dfs(n) for n in graph)
'''),

    H2("4.5 Çok örnekli kaynaklar için detection algoritması"),
    P("Ders kitabındaki bu algoritma şunu sorar: \"Şu an boşta olan kaynaklarla, isteği karşılanabilecek "
      "bir process var mı? Varsa onu bitmiş say, kaynaklarını geri al ve tekrar sor.\" Sonunda bitmiş "
      "sayılamayan process'ler deadlock'tadır."),
    Code('''
Work   = Available                  (boştaki kaynakların kopyası)
Finish = her process için False     (hiç kaynak tutmuyorsa True)

tekrarla:
    Finish[i] == False  VE  Request[i] <= Work  olan bir i bul
    bulunduysa:  Work = Work + Allocation[i]      (i bitti, kaynaklarını bıraktı)
                 Finish[i] = True
    bulunamadıysa: dur

Finish[i] == False kalan her process deadlock'tadır.
'''),
    Box("ornek", ["<b>Örnek 1 (deadlock yok):</b> 3.2'deki tablo, Available = [0, 0].",
                  "• P1'in isteği [0, 0] ≤ [0, 0] → P1 biter, Work = [0,0] + [1,0] = [1, 0]",
                  "• P2'nin isteği [1, 0] ≤ [1, 0] → P2 biter, Work = [1,0] + [1,1] = [2, 1]",
                  "• P3'ün isteği [0, 1] ≤ [2, 1] → P3 biter. Herkes bitti: <b>deadlock yok</b> (sıra: P1, P2, P3).",
                  "<b>Örnek 2 (deadlock var):</b> Aynı tablo, ama P1 de bir tarayıcı istiyor: Request(P1) = [0, 1].",
                  "• Work = [0, 0]. P1 [0,1], P2 [1,0], P3 [0,1] isteklerinden hiçbiri karşılanamaz.",
                  "• Hiçbiri bitemez: <b>P1, P2 ve P3 deadlock'ta.</b>"]),
    Box("dikkat", "\"[1, 0] ≤ [2, 1]\" ifadesi vektörlerin <b>her elemanı ayrı ayrı</b> küçük eşit demektir: "
        "1 ≤ 2 ve 0 ≤ 1. Bir eleman bile büyükse karşılaştırma yanlıştır."),

    H2("4.6 Tespit ne zaman çalıştırılır?"),
    P("Gerçek sistemlerde tespit pahalı olduğu için belirli aralıklarla çalıştırılır. Bizim simülasyonumuz "
      "küçük olduğu için <b>her request işleminden sonra</b> çalıştırabiliriz; böylece deadlock oluştuğu an "
      "yakalanır."),
    Box("tanim", "<b>Birim testi (unit test):</b> kodun tek bir parçasını (ör. <i>has_cycle</i> fonksiyonu) "
        "tek başına, bilinen bir girdiyle çalıştırıp beklenen çıktıyı verip vermediğini kontrol eden küçük "
        "programdır. Ayrıntısı Bölüm 10'da."),
    Box("ozet", B(["Graf, düğüm, kenar, yönlü graf ve döngü kavramlarını",
                   "RAG'de request ve assignment kenarlarını, çizim kurallarını",
                   "Döngü ile deadlock arasındaki ilişkiyi (altın kural) ve Şekil 3'teki istisnayı",
                   "Wait-for graph'ı",
                   "DFS'in üç renkle döngüyü nasıl bulduğunu",
                   "Detection algoritmasını elle bir tablo üzerinde çalıştırabilmeyi"], "bbul")),
]

# ============================================================
story += H1("5. Hafta — Görselleştirme", "İlişkileri bir bakışta anlaşılır göstermek")
story += [
    H2("5.1 Neden görselleştirme?"),
    P("Tablolar doğrudur ama okunması zordur. Aynı bilgi RAG olarak çizildiğinde döngü göze hemen çarpar. "
      "Projemizi bir algoritma ödevinden ayıran şeylerden biri de, kullanıcının neler olup bittiğini "
      "görebilmesidir."),
    H2("5.2 Çizim kuralları"),
    T([["Öğe", "Gösterim"],
       ["Process", "Daire; içinde adı (P1)"],
       ["Kaynak", "Kare; üstünde adı (R1), içinde her örnek için bir nokta"],
       ["Atama kenarı", "Kaynaktan process'e ok"],
       ["İstek kenarı", "Process'ten kaynağa ok (tercihen kesikli çizgi)"],
       ["Deadlock döngüsü", "Kırmızı; döngüdeki düğümler vurgulanır"],
       ["Process durumu", "Renk kodu: RUNNING yeşil, WAITING turuncu, TERMINATED gri"]], [0.3, 0.7]),
    H2("5.3 Graf yerleşimi (layout)"),
    Box("tanim", "<b>Layout</b>, düğümlerin ekranda nereye konacağına karar veren yöntemdir. Elle koordinat "
        "vermek yerine kütüphaneler bunu otomatik yapar; örneğin <i>force-directed</i> yerleşim, düğümleri "
        "birbirini iten mıknatıslar, kenarları yaylar gibi düşünerek dengeli bir görüntü üretir."),
    H2("5.4 Kullanılabilecek araçlar"),
    T([["Araç", "Ne işe yarar?", "Hangi arayüzle?"],
       ["networkx", "Python'da graf veri yapısı ve algoritmaları; döngü bulma dahil", "Her ikisi"],
       ["matplotlib", "Grafı resim olarak çizme", "PyQt içine gömülebilir"],
       ["PyQt QGraphicsView", "Etkileşimli, tıklanabilir çizim alanı", "PyQt"],
       ["vis-network / Cytoscape.js", "Tarayıcıda etkileşimli graf", "Web"]], [0.25, 0.5, 0.25]),
    Box("dikkat", "networkx'in hazır döngü fonksiyonları var, ama projenin değerlendirilen kısmı algoritmayı "
        "<b>bizim</b> yazmamız. Hazır fonksiyonları yalnızca kendi kodumuzun sonucunu test etmek için "
        "karşılaştırma amacıyla kullanmak doğru olur."),
    Box("proje", "Arayüz teknolojisi (PyQt mı web mi) henüz seçilmedi; Bölüm 9'daki karşılaştırmaya bakarak "
        "5. haftadan önce karar vermemiz gerekiyor, çünkü çizim kodu buna göre yazılacak."),
    Box("ozet", B(["RAG'in ekranda nasıl çizileceğini (şekil ve renk kuralları)",
                   "Layout kavramını",
                   "Hangi araçların ne işe yaradığını ve hazır algoritma kullanmanın sınırını"], "bbul")),
]

# ============================================================
story += H1("6. Hafta — Risk Analizi: Güvenli Durum ve Banker's Algorithm",
            "Deadlock oluşmadan önce tehlikeyi görmek (avoidance)")
story += [
    H2("6.1 Avoidance fikri"),
    P("Tespit (Hafta 4), deadlock <b>olduktan sonra</b> çalışır. Avoidance ise her kaynak isteğinde "
      "\"bu isteği verirsem sistem ileride kilitlenebilir mi?\" diye önceden hesaplar. Tehlikeliyse isteği "
      "o an vermez, process biraz bekler."),

    H2("6.2 Güvenli durum (safe state)"),
    Box("tanim", ["<b>Güvenli durum:</b> Process'leri bir sıraya dizip, her birinin en kötü ihtimalle "
                  "ihtiyacının tamamını alarak bitebileceği bir sıra varsa, sistem güvenli durumdadır.",
                  "<b>Güvenli sıra (safe sequence):</b> bu bitirme sırasının kendisidir (ör. &lt;P1, P2, P3&gt;).",
                  "<b>Güvensiz durum (unsafe state):</b> böyle bir sıra yoksa."]),
    Box("dikkat", "Güvensiz durum, deadlock <b>demek değildir</b>. Güvensiz durum \"deadlock olma ihtimali "
        "var\" demektir. İlişki şöyledir: tüm deadlock'lar güvensizdir ama tüm güvensiz durumlar deadlock "
        "değildir. Güvenli durumdaysak ise deadlock kesinlikle olmaz."),
    Box("ornek", "Banka benzetmesi (algoritmanın adı buradan gelir): Bankacının 10 lirası var ve üç müşteriye "
        "kredi limiti tanımış. Bankacı, bir müşteriye para verirken \"bu parayı verdikten sonra, en azından "
        "bir müşterinin limitinin tamamını karşılayıp parasını geri alabilir miyim, sonra ondan gelenle "
        "diğerini...\" diye düşünür. Herkesi sırayla tamamlayabileceği bir yol varsa parayı verir."),

    H2("6.3 Gerekli yapılar"),
    P("Banker's Algorithm, 3. haftadaki yapılara iki tane daha ekler:"),
    Code("Max[i]  = process i'nin her kaynaktan en fazla kaç adete ihtiyacı olacağı (baştan bildirir)\n"
         "Need[i] = Max[i] − Allocation[i]   (daha ne kadar isteyebilir)"),
    Box("dikkat", "Algoritmanın en önemli şartı, her process'in <b>maksimum ihtiyacını önceden bildirmesidir</b>. "
        "Gerçek hayatta bu çoğu zaman bilinmez; algoritmanın pratikteki zayıflığı budur. Simülasyonumuzda "
        "bunu senaryo dosyasında her process için yazacağız."),

    H2("6.4 Safety (güvenlik) algoritması"),
    Code('''
Work   = Available
Finish = her process için False

tekrarla:
    Finish[i] == False  VE  Need[i] <= Work  olan bir i bul
    bulunduysa:  Work = Work + Allocation[i]
                 Finish[i] = True,  i'yi güvenli sıraya ekle
    bulunamadıysa: dur

Herkes True ise → GÜVENLİ (bulunan sıra güvenli sıradır), değilse → GÜVENSİZ
'''),
    Box("dikkat", "Detection algoritması ile neredeyse aynıdır. Tek fark: detection <b>Request</b> ile "
        "(şu an istediği), safety <b>Need</b> ile (en kötü ihtimalle isteyebileceği) karşılaştırır. "
        "Bu yüzden iki algoritma aynı yardımcı fonksiyonu paylaşabilir."),

    H2("6.5 Çalışılmış örnek"),
    P("Kaynaklar: R1 toplam 6, R2 toplam 4."),
    T([["Process", "Max (R1, R2)", "Allocation", "Need = Max − Allocation"],
       ["P1", "4, 2", "2, 1", "2, 1"],
       ["P2", "3, 2", "1, 1", "2, 1"],
       ["P3", "4, 3", "1, 1", "3, 2"]], [0.16, 0.24, 0.24, 0.36]),
    P("Tahsis edilen toplam: [4, 3] → <b>Available = [6−4, 4−3] = [2, 1]</b>."),
    Box("ornek", ["<b>Safety kontrolü:</b> Work = [2, 1]",
                  "• P1: Need [2, 1] ≤ [2, 1] (uygun) → Work = [2,1] + [2,1] = [4, 2]",
                  "• P2: Need [2, 1] ≤ [4, 2] (uygun) → Work = [4,2] + [1,1] = [5, 3]",
                  "• P3: Need [3, 2] ≤ [5, 3] (uygun) → Work = [5,3] + [1,1] = [6, 4]",
                  "Sonuç: <b>GÜVENLİ</b>, güvenli sıra &lt;P1, P2, P3&gt;."]),

    H2("6.6 Resource-request algoritması"),
    P("Bir process kaynak istediğinde üç adım uygulanır:"),
] + B(["<b>Adım 1:</b> İstek, bildirdiği ihtiyaçtan büyükse (Request > Need) → hata; process yalan söylüyor.",
       "<b>Adım 2:</b> İstek, boştaki kaynaktan büyükse (Request > Available) → process beklemeli.",
       "<b>Adım 3:</b> Kaynağı <b>verilmiş gibi</b> yap (Available −, Allocation +, Need −) ve safety "
       "algoritmasını çalıştır. Güvenliyse ver; güvensizse eski haline döndür ve process'i beklet."]) + [
    Box("ornek", ["<b>P3, [1, 0] istiyor:</b> [1,0] ≤ Need [3,2] (uygun), [1,0] ≤ Available [2,1] (uygun).",
                  "Verilmiş gibi yap: Available = [1, 1], Allocation(P3) = [2, 1], Need(P3) = [2, 2].",
                  "Safety: Work = [1, 1]. P1 Need [2,1] (uygun değil), P2 [2,1] (uygun değil), P3 [2,2] (uygun değil) → kimse bitemiyor.",
                  "Sonuç: <b>GÜVENSİZ</b> → istek reddedilir, P3 bekler.",
                  "<b>P1, [1, 0] istiyor:</b> Available = [1, 1], Allocation(P1) = [3, 1], Need(P1) = [1, 1].",
                  "Safety: P1 [1,1] ≤ [1,1] (uygun) → Work = [4, 2]; P2 (uygun) → [5, 3]; P3 (uygun) → [6, 4].",
                  "Sonuç: <b>GÜVENLİ</b> → istek verilir."]),
    Box("proje", "Banker's'ı katı bir kapı gibi kullanmak yerine <b>uyarı</b> aracı olarak kullanacağız: "
        "güvensiz bir istek geldiğinde kullanıcıya \"bu istek sistemi güvensiz duruma sokuyor\" diyeceğiz. "
        "Böylece demoda kullanıcı uyarıyı görmezden gelip deadlock'un oluşmasını da izleyebilecek."),
    Box("ozet", B(["Avoidance ile detection farkını",
                   "Güvenli durum, güvenli sıra ve güvensiz durum tanımlarını; güvensiz ≠ deadlock",
                   "Max ve Need yapılarını, Need'in hesabını",
                   "Safety algoritmasını elle çalıştırabilmeyi",
                   "Resource-request algoritmasının üç adımını",
                   "Banker's'ın pratikteki sınırlılığını (maksimum ihtiyacın önceden bilinmesi)"], "bbul")),
]

# ============================================================
story += H1("7. Hafta — Risk Seviyesi Sistemi", "Riski derecelendirmek ve nedenini açıklamak")
story += [
    P("Bu bölüm ders kitabında hazır bulunmaz; <b>projemizin kendi tasarımıdır</b> ve özgünlüğümüzün önemli "
      "bir kısmı buradadır. Aşağıdaki kurallar bir başlangıç önerisidir; eşik değerlerine 7. haftada ekip "
      "olarak birlikte karar vereceğiz."),
    H2("7.1 Neden seviyelere ihtiyaç var?"),
    P("Banker's Algorithm yalnızca iki cevap verir: güvenli ya da güvensiz. Kullanıcı için daha faydalı olan, "
      "\"ne kadar tehlikedeyiz ve neden?\" sorusunun cevabıdır. Hava durumundaki sarı-turuncu-kırmızı uyarılar "
      "gibi düşünün."),
    H2("7.2 Önerilen seviyeler"),
    T([["Seviye", "Koşul (öneri)", "Kullanıcıya mesaj örneği"],
       ["LOW", "Bekleyen process yok ya da boş kaynak bol; sistem güvenli.", "Sistem normal çalışıyor."],
       ["MEDIUM", "Sistem güvenli ama bekleyen process var ve boş kaynak az (ör. %20'nin altı) ya da en az iki halkalı bir bekleme zinciri oluşmuş.", "P2, P1'i bekliyor; boş kaynak azaldı."],
       ["HIGH", "Sistem güvensiz durumda (Banker's güvenli sıra bulamıyor) ama henüz deadlock yok.", "R2 isteği sistemi güvensiz duruma soktu. P1 ve P3 birbirini bekleyebilir."],
       ["CRITICAL", "Detection algoritması deadlock buldu.", "DEADLOCK: P1 → R2 → P2 → R1 → P1"]],
      [0.14, 0.50, 0.36]),
    H2("7.3 Risk nedenini açıklamak"),
    P("Her uyarı, nedenini söylemelidir. Bunun için risk hesaplanırken hangi kuralın tetiklendiği de kaydedilir. "
      "Proje belgesindeki örnek mesaj: <i>\"P2 ve P4 karşılıklı kaynak bekliyor.\"</i>"),
    Box("tanim", "<b>Heuristic (sezgisel kural):</b> kesin matematiksel garanti vermeyen ama pratikte iyi "
        "sonuç veren kural. Risk seviyelerimiz bir heuristic'tir; raporda bunu açıkça belirtmeliyiz."),
    H2("7.4 Zaman içindeki değişim"),
    P("Risk seviyesi her adımdan sonra kaydedilirse, demoda \"LOW → MEDIUM → HIGH → CRITICAL → (recovery) → LOW\" "
      "geçişi bir zaman çizelgesinde gösterilebilir. Final demo senaryosundaki \"sistem risk artışını gösteriyor\" "
      "adımı tam olarak budur."),
    Box("ozet", B(["Risk seviyelerinin neden Banker's'ın tek başına veremediği bilgiyi sunduğunu",
                   "Dört seviyenin önerilen koşullarını",
                   "Her uyarının bir neden içermesi gerektiğini",
                   "Heuristic kavramını ve kuralların ekip kararı olduğunu"], "bbul")),
]

# ============================================================
story += H1("8. Hafta — Recovery (Kurtarma)", "Deadlock'tan sonra sistemi tekrar çalışır hale getirmek")
story += [
    P("Deadlock bir kez oluştuysa, dört koşuldan birini zorla kırmak gerekir. Ders kitabı iki yol önerir: "
      "process'leri sonlandırmak ya da kaynakları geri almak."),
    H2("8.1 Yöntem 1: Process sonlandırma (process termination)"),
    T([["Yaklaşım", "Nasıl?", "Artısı / eksisi"],
       ["Hepsini sonlandır", "Deadlock'taki tüm process'ler sonlandırılır.", "Kesin ve hızlı çözer; ama yapılan tüm iş kaybolur."],
       ["Birer birer sonlandır", "Bir process sonlandırılır, tespit tekrar çalıştırılır; deadlock sürüyorsa bir sonraki...", "Daha az iş kaybı; ama her seferinde tespit tekrar çalışır."]],
      [0.22, 0.43, 0.35]),
    H2("8.2 Kurban seçimi (victim selection)"),
    Box("tanim", "<b>Kurban (victim):</b> deadlock'u çözmek için sonlandırılacak ya da kaynağı elinden "
        "alınacak process. Amaç, <b>en düşük maliyetli</b> kurbanı seçmektir."),
    P("Ders kitabının maliyet ölçütleri:"),
] + B(["Process'in önceliği (önemli process'ler korunur)",
       "Ne kadar süredir çalıştığı ve bitmesine ne kadar kaldığı",
       "Kaç kaynak tuttuğu (çok kaynak tutan, sonlanınca çok kaynak serbest bırakır)",
       "Bitirmek için kaç kaynağa daha ihtiyacı olduğu",
       "Deadlock'u çözmek için kaç process'in sonlandırılması gerekeceği"]) + [
    Box("ornek", ["Simülasyon için basit bir maliyet formülü önerisi:",
                  "<i>maliyet = öncelik × 10 + tuttuğu kaynak sayısı × (−2) + daha önce kurban seçilme sayısı × 5</i>",
                  "Döngüdeki process'lerin maliyeti hesaplanır, en düşük olan sonlandırılır. Formüldeki "
                  "katsayılar örnektir; 8. haftada birlikte belirleyeceğiz."]),
    H2("8.3 Yöntem 2: Kaynak geri alma (resource preemption)"),
    P("Process'i tamamen öldürmek yerine elindeki bir kaynağı alıp başkasına vermek. Üç sorunu vardır:"),
    T([["Sorun", "Açıklama"],
       ["Kurban seçimi", "Kimden, hangi kaynağı alacağız? (yukarıdaki maliyet mantığı)"],
       ["Rollback (geri sarma)", "Kaynağı alınan process eski bir güvenli noktaya geri döndürülmelidir; en basiti baştan başlatmaktır."],
       ["Starvation", "Hep aynı process kurban seçilirse hiç bitemez. Çözüm: kurban seçilme sayısını maliyete eklemek."]],
      [0.25, 0.75]),
    H2("8.4 Kurtarmadan sonra doğrulama"),
    P("Kurtarma uygulandıktan sonra detection algoritması <b>tekrar çalıştırılır</b>. Deadlock kalmadıysa "
      "sistem SAFE durumuna döndü demektir ve risk seviyesi düşer. Bu doğrulama adımı, final demonun son "
      "adımıdır."),
    Box("proje", "Arayüzde deadlock oluştuğunda kullanıcıya seçenekler sunulacak: \"P2'yi sonlandır (maliyet: 12)\", "
        "\"P1'i sonlandır (maliyet: 18)\", \"R1'i P2'den geri al\". En düşük maliyetli seçenek önerilen olarak işaretlenecek."),
    Box("ozet", B(["İki kurtarma yöntemini ve farklarını",
                   "Hepsini sonlandırma ile birer birer sonlandırma farkını",
                   "Kurban seçim ölçütlerini ve maliyet mantığını",
                   "Rollback ve starvation sorunlarını",
                   "Kurtarmadan sonra neden tespitin tekrar çalıştırıldığını"], "bbul")),
]

# ============================================================
story += H1("9. Hafta — Kullanıcı Arayüzü ve Yazılım Mimarisi", "Tüm modülleri tek ekranda birleştirmek")
story += [
    H2("9.1 Katmanlı mimari ve sorumlulukların ayrılması"),
    Box("tanim", "<b>Separation of concerns (sorumlulukların ayrılması):</b> her modülün yalnızca kendi işini "
        "yapması. Simülasyon motoru ekranı bilmez; arayüz algoritmaları bilmez, sadece motora sorar."),
    P("Bu ayrım bize üç şey kazandırır: (1) dört kişi aynı anda çalışabilir, (2) algoritmalar arayüz olmadan "
      "test edilebilir, (3) arayüz değişse bile (PyQt → web) motor aynı kalır. Şekil 0'daki katmanlar bu "
      "ilkeye göre çizilmiştir."),
    Box("tanim", "<b>MVC (Model-View-Controller):</b> yaygın bir arayüz mimarisi. <b>Model</b> veriyi ve "
        "kuralları tutar (simülasyon motoru), <b>View</b> ekranı çizer, <b>Controller</b> kullanıcının "
        "tıklamalarını modele iletir."),
    H2("9.2 Olay güdümlü programlama"),
    Box("tanim", "<b>Event-driven (olay güdümlü) programlama:</b> programın yukarıdan aşağı akmak yerine "
        "olayları (tıklama, zamanlayıcı, yeni log satırı) bekleyip her olaya tepki verdiği yapı. "
        "Tüm arayüz kütüphaneleri böyle çalışır."),
    P("Örnek: kullanıcı \"P1, R2'yi istesin\" butonuna tıklar → controller motora <i>request</i> çağrısı yapar "
      "→ motor durumu günceller, tespit ve risk hesaplanır → arayüz yeni durumu çizer."),
    H2("9.3 Dashboard'da olacaklar"),
] + B(["Özet kartları: aktif process sayısı, kaynak sayısı, anlık risk seviyesi",
       "Process listesi (durum renkleriyle) ve kaynak listesi (sahibi, kuyruğu)",
       "RAG çizimi (Hafta 5)",
       "Deadlock uyarısı ve recovery seçenekleri (Hafta 8)",
       "Olay akışı (log) ve senaryo yükle / adım adım ilerlet butonları"]) + [
    H2("9.4 PyQt mi, web mi?"),
    T([["Ölçüt", "PyQt (masaüstü)", "Web (Python sunucu + tarayıcı)"],
       ["Öğrenilecek dil", "Yalnızca Python", "Python + HTML/CSS/JavaScript"],
       ["Kurulum", "pip install PyQt6", "Flask/FastAPI + ön yüz kütüphaneleri"],
       ["Graf çizimi", "QGraphicsView veya matplotlib", "vis-network, Cytoscape.js (çok güçlü)"],
       ["Görünüm", "Klasik masaüstü uygulaması", "Modern, esnek tasarım"],
       ["Demo", "Uygulamayı açmak yeterli", "Sunucuyu başlatıp tarayıcıda açmak gerekir"],
       ["Ekip için zorluk", "Daha az hareketli parça", "İki dünya (sunucu + tarayıcı) arasında iletişim"]],
      [0.2, 0.38, 0.42]),
    Box("proje", "Karar henüz verilmedi. Ekibin JavaScript bilgisi azsa PyQt daha düz bir yoldur; görsel "
        "etkileyicilik öncelikliyse web daha çok imkân sunar. Bu kararı 5. haftadan önce birlikte vereceğiz."),
    Box("ozet", B(["Sorumlulukların ayrılması ilkesini ve bize ne kazandırdığını",
                   "MVC'deki üç parçanın görevini",
                   "Olay güdümlü programlamayı",
                   "PyQt ve web seçeneklerinin artı ve eksilerini"], "bbul")),
]

# ============================================================
story += H1("10. Hafta — Test ve İyileştirme", "Sistemin doğru ve kararlı çalıştığını kanıtlamak")
story += [
    H2("10.1 Test türleri"),
    T([["Test türü", "Neyi test eder?", "Projemizde örnek"],
       ["Unit test (birim testi)", "Tek bir fonksiyon ya da sınıf", "has_cycle, safety fonksiyonları"],
       ["Integration test (entegrasyon)", "Modüllerin birlikte çalışması", "Motor + tespit: request sonrası deadlock bulunuyor mu?"],
       ["System test (sistem testi)", "Uygulamanın baştan sona davranışı", "Senaryo dosyası yüklenip arayüzde doğru sonuç görülüyor mu?"],
       ["Regression test (gerileme)", "Yeni değişikliğin eski özellikleri bozmadığı", "Recovery eklendikten sonra tespit testleri hâlâ geçiyor mu?"]],
      [0.26, 0.32, 0.42]),
    H2("10.2 Test senaryosu nasıl yazılır?"),
    P("Her test üç parçadan oluşur: <b>hazırlık</b> (başlangıç durumu), <b>eylem</b> (yapılan işlem) ve "
      "<b>beklenen sonuç</b>. Test, gerçek sonuç beklenenle aynıysa geçer."),
    T([["No", "Senaryo", "Beklenen sonuç"],
       ["1", "Normal çalışma: process'ler kaynakları sırayla alıp bırakıyor", "Deadlock yok, risk LOW"],
       ["2", "Tek deadlock: P1-R1-P2-R2 çapraz istek", "P1 ve P2 deadlock'ta, risk CRITICAL"],
       ["3", "Çoklu deadlock: iki ayrı döngü", "İki döngü ayrı ayrı raporlanıyor"],
       ["4", "Recovery: senaryo 2 + kurban sonlandırma", "Deadlock kalmadı, sistem SAFE"],
       ["5", "Şekil 3 durumu: döngü var ama deadlock yok", "Deadlock yok (en sık yapılan hatayı yakalar)"]],
      [0.07, 0.55, 0.38]),
    H2("10.3 pytest ile birim testi"),
    Box("tanim", "<b>pytest</b>, Python'un en yaygın test aracıdır. Adı <i>test_</i> ile başlayan fonksiyonları "
        "bulup çalıştırır; <i>assert</i> satırı yanlışsa testi başarısız sayar."),
    Code('''
from detection import has_cycle

def test_iki_process_deadlock():
    graph = {"P1": ["R2"], "R2": ["P2"], "P2": ["R1"], "R1": ["P1"]}
    assert has_cycle(graph) is True

def test_dongu_yok():
    graph = {"P1": ["R1"], "R1": []}
    assert has_cycle(graph) is False
'''),
    Code("$ pytest\n====== 2 passed in 0.01s ======"),
    H2("10.4 Uç durumlar (edge cases)"),
    P("Hataların çoğu \"normal\" durumlarda değil, uçlarda çıkar. Mutlaka denenmesi gerekenler:"),
] + B(["Hiç process ya da kaynak yokken",
       "Bir process kendi tuttuğu kaynağı tekrar isterse",
       "Tutmadığı bir kaynağı bırakmaya çalışırsa",
       "Sonlandırılmış (TERMINATED) bir process işlem yapmaya çalışırsa",
       "Kaynağın toplam adedinden fazlası istenirse"]) + [
    Box("tanim", "<b>Debugging (hata ayıklama):</b> hatanın nedenini bulma süreci. Önce hatayı tekrar üretin, "
        "sonra log'a bakın, sonra düzeltip aynı hatayı yakalayan bir test ekleyin; böylece hata bir daha geri "
        "gelmez."),
    Box("ozet", B(["Dört test türünü ve farklarını",
                   "Bir test senaryosunun üç parçasını",
                   "pytest ile basit bir birim testinin nasıl yazılıp çalıştırıldığını",
                   "Uç durumların neden önemli olduğunu"], "bbul")),
]

# ============================================================
story += H1("11. Hafta — Final: Demo, Rapor ve Sunum", "Projeyi baştan sona çalışır halde sunmak")
story += [
    H2("11.1 Final demo senaryosu"),
] + B(["Sistemi açıyoruz; üç process ve üç kaynak oluşturuyoruz.",
       "Kaynakları dağıtıyoruz; risk LOW.",
       "İki process'in birbirini beklediği senaryoyu kuruyoruz; risk önce MEDIUM, sonra HIGH oluyor.",
       "Deadlock oluşuyor; risk CRITICAL, döngü grafikte kırmızı.",
       "Sistem döngüdeki process ve kaynakları gösteriyor, recovery seçeneklerini sunuyor.",
       "Önerilen kurbanı sonlandırıyoruz; kaynaklar serbest kalıyor, sistem SAFE durumuna dönüyor."]) + [
    Box("dikkat", ["Canlı demoda en sık yaşanan sorun, o an beklenmeyen bir hatadır. Önlem olarak:",
                   "• Demo senaryosunu JSON dosyası olarak hazırlayın, elle tıklamaya güvenmeyin.",
                   "• En az iki kez prova edin, bir kez de başka bir bilgisayarda.",
                   "• Yedek olarak demonun ekran kaydını hazırlayın."]),
    H2("11.2 Proje raporunun bölümleri"),
    T([["Bölüm", "İçerik"],
       ["Özet", "Projenin yarım sayfalık özeti"],
       ["Giriş ve problem tanımı", "Deadlock nedir, neden önemli, projenin amacı"],
       ["Teorik arka plan", "Coffman koşulları, RAG, detection, Banker's, recovery (bu kitaptan yararlanılabilir)"],
       ["Tasarım", "Mimari şema, sınıflar, veri yapıları, arayüz tasarımı"],
       ["Gerçekleştirme", "Her modülün nasıl kodlandığı, önemli kod parçaları"],
       ["Test ve sonuçlar", "Test senaryoları, sonuç tablosu, ekran görüntüleri"],
       ["Sonuç ve gelecek çalışmalar", "Neler başarıldı, eksikler, gerçek sisteme entegrasyon fikri"],
       ["Kaynakça", "Silberschatz ve kullanılan diğer kaynaklar"],
       ["Ekip katkıları", "Kim hangi modülü yaptı"]], [0.3, 0.7]),
    H2("11.3 Sunum ipuçları"),
] + B(["Her ekip üyesi kendi modülünü anlatsın; hoca herkesin projeyi anladığını görmek ister.",
       "Teoriyi az, demoyu çok tutun: önce 2-3 slaytla problem, sonra canlı demo.",
       "Şekil 2'deki gibi basit bir örnekle başlayın; herkes döngüyü görsün.",
       "Sorulabilecek sorulara hazırlanın: \"Döngü her zaman deadlock mıdır?\", \"Banker's neden pratikte az kullanılır?\", "
       "\"Kurbanı neye göre seçtiniz?\"."]) + [
    Box("ozet", B(["Demo akışını ve risklerine karşı önlemleri",
                   "Raporun bölümlerini",
                   "Sunumda sorulabilecek temel soruların cevaplarını"], "bbul")),
]

# ============================================================
story += H1("Ek A — Yazılım Mühendisliği Pratikleri", "Gereksinimler, Git ve ekip çalışması")
story += [
    H2("A.1 Gereksinimler"),
    Box("tanim", ["<b>Fonksiyonel gereksinim:</b> sistemin <b>ne yapacağı</b>.",
                  "<b>Fonksiyonel olmayan gereksinim:</b> sistemin <b>nasıl</b> olacağı (hız, kullanılabilirlik, taşınabilirlik)."]),
    T([["Tür", "Deadlock Guardian'dan örnekler"],
       ["Fonksiyonel", "Sistem process ve kaynak oluşturabilmelidir. · Deadlock'u tespit edip döngüyü göstermelidir. · "
                       "Güvensiz isteklerde uyarı vermelidir. · En az bir recovery yöntemi uygulamalıdır."],
       ["Fonksiyonel olmayan", "Tespit sonucu 1 saniyeden kısa sürede gösterilmelidir. · Arayüz ilk kez kullanan biri "
                               "tarafından anlaşılabilmelidir. · Windows ve macOS'ta çalışmalıdır. · Kod modüler olmalıdır."]],
      [0.22, 0.78]),
    H2("A.2 Git ve GitHub"),
    T([["Kavram", "Anlamı"],
       ["Repository (depo)", "Projenin tüm dosyalarını ve tüm geçmişini tutan klasör"],
       ["Commit", "Değişikliklerin açıklamalı bir anlık kaydı (\"Resource sınıfına kuyruk eklendi\")"],
       ["Branch (dal)", "Ana koddan ayrılıp bağımsız çalışılan kopya"],
       ["Merge (birleştirme)", "Bir dalın değişikliklerini başka dala katmak"],
       ["Pull request (PR)", "\"Dalımı ana koda katmak istiyorum\" talebi; ekip inceler, onaylar"],
       ["Merge conflict (çakışma)", "İki kişi aynı satırı farklı değiştirdiğinde Git'in karar verememesi; elle çözülür"],
       ["Clone / pull / push", "Depoyu indirmek / güncellemeleri almak / kendi commit'lerini göndermek"]],
      [0.28, 0.72]),
    H2("A.3 Dört kişilik ekip için önerilen çalışma düzeni"),
] + B(["<b>main</b> dalı her zaman çalışan kodu tutar; kimse doğrudan main'e yazmaz.",
       "Herkes kendi işi için dal açar: <i>feature/simulasyon</i>, <i>feature/tespit</i>, <i>feature/risk</i>, <i>feature/arayuz</i>.",
       "Küçük ve sık commit atılır; mesaj ne yapıldığını söyler.",
       "İş bitince pull request açılır, en az bir ekip arkadaşı inceler (code review), sonra main'e birleştirilir.",
       "Haftada bir ortak toplantıda dallar birleştirilir ve o haftanın çıktısı birlikte çalıştırılır.",
       "Her modülün testleri main'e birleştirmeden önce geçmelidir."]) + [
    H2("A.4 Önerilen klasör yapısı"),
    Code('''
deadlock-guardian/
├── src/
│   ├── simulation/     # Process, Resource, motor        (Üye 1)
│   ├── detection/      # RAG, DFS, detection algoritması (Üye 2)
│   ├── risk/           # Banker's, risk seviyeleri       (Üye 3)
│   ├── recovery/       # kurban seçimi, kurtarma         (Üye 2)
│   └── ui/             # arayüz ve çizim                 (Üye 4)
├── scenarios/          # JSON senaryo dosyaları
├── tests/              # pytest testleri
├── README.md
└── requirements.txt    # kullanılan Python paketleri
'''),
]

# ============================================================
story += H1("Ek B — Python Hızlı Başvuru", "Projede en çok kullanacağımız yapılar")
story += [
    T([["Yapı", "Örnek", "Ne işe yarar?"],
       ["Liste (list)", "held = [\"R1\", \"R2\"]", "Sıralı eleman topluluğu; append, remove"],
       ["Sözlük (dict)", "alloc = {\"P1\": [1, 0]}", "Anahtar → değer eşlemesi; tablolar için ideal"],
       ["Küme (set)", "visited = set()", "Tekrarsız eleman topluluğu; \"daha önce gördük mü?\""],
       ["deque", "q = deque(); q.append(p); q.popleft()", "Hızlı kuyruk (FIFO)"],
       ["Enum", "class State(Enum): RUNNING = 1", "Sabit değer listesi; yazım hatasını önler"],
       ["Sınıf", "class Process: def __init__(self, pid): ...", "Nesne kalıbı"],
       ["f-string", "f\"{p.pid} bekliyor\"", "Değişkenleri metne yerleştirme"],
       ["Liste üreteci", "[p for p in procs if p.state == WAITING]", "Filtrelenmiş yeni liste"],
       ["any / all", "all(x <= y for x, y in zip(a, b))", "Vektör karşılaştırması (4.5 ve 6.4)"],
       ["json", "data = json.load(open(\"senaryo.json\"))", "Senaryo dosyası okuma"]],
      [0.17, 0.43, 0.40]),
    Box("ornek", ["Bölüm 4 ve 6'daki \"vektör ≤ vektör\" karşılaştırmasının Python hali:",
                  Preformatted("def kucuk_esit(a, b):\n    return all(x <= y for x, y in zip(a, b))\n\n"
                               "kucuk_esit([1, 0], [2, 1])   # True\nkucuk_esit([3, 2], [2, 1])   # False",
                               st["code"])]),
]

# ============================================================
story += H1("Ek C — Sözlük", "Türkçe - İngilizce terimler")
gloss = [
    ("Atama kenarı", "Assignment edge", "Kaynaktan process'e ok; kaynak verilmiş"),
    ("Bekleme", "Waiting", "Process'in bir kaynağı beklediği durum"),
    ("Birim testi", "Unit test", "Tek bir fonksiyonun tek başına test edilmesi"),
    ("Derinlik öncelikli arama", "Depth-first search (DFS)", "Grafı derinlemesine gezme algoritması"),
    ("Döngü", "Cycle", "Okları takip ederek başlangıç düğümüne dönebilmek"),
    ("Döngüsel bekleme", "Circular wait", "Process'lerin kapalı bir zincirde birbirini beklemesi"),
    ("Geri alınamazlık", "No preemption", "Kaynağın sahibinden zorla alınamaması"),
    ("Geri alma (kaynak)", "Resource preemption", "Kaynağı bir process'ten alıp başkasına vermek"),
    ("Geri sarma", "Rollback", "Process'i daha önceki güvenli bir noktaya döndürmek"),
    ("Görmezden gelme", "Ignore / ostrich approach", "Deadlock için hiçbir şey yapmamak"),
    ("Güvenli durum", "Safe state", "Herkesin bitebileceği bir sıranın bulunduğu durum"),
    ("Güvenli sıra", "Safe sequence", "Process'lerin sorunsuz bitebileceği sıra"),
    ("Güvensiz durum", "Unsafe state", "Güvenli sıra bulunamayan durum (deadlock riski)"),
    ("Açlık", "Starvation", "Bir process'in sırasının hiç gelmemesi"),
    ("İstek kenarı", "Request edge", "Process'ten kaynağa ok; kaynak isteniyor"),
    ("Kaçınma", "Avoidance", "İstekleri güvenliyse vermek (Banker's)"),
    ("Kaynak", "Resource", "Process'in ihtiyaç duyduğu sınırlı şey"),
    ("Kaynak örneği / adedi", "Instance", "Bir kaynak tipinin birbirinin aynısı kopyalarından biri"),
    ("Kaynak tahsis grafı", "Resource Allocation Graph (RAG)", "Process-kaynak ilişkilerinin yönlü grafı"),
    ("Kaynak tahsisi", "Resource allocation", "Kaynakların process'lere dağıtılması"),
    ("Karşılıklı dışlama", "Mutual exclusion", "Kaynağı aynı anda tek process'in kullanabilmesi"),
    ("Kilitlenme", "Deadlock", "Process'lerin birbirini sonsuza kadar beklemesi"),
    ("Kurban", "Victim", "Kurtarmada sonlandırılan / kaynağı alınan process"),
    ("Kurtarma", "Recovery", "Deadlock'tan sonra sistemi çalışır hale getirmek"),
    ("Kuyruk", "Queue (FIFO)", "İlk gelenin ilk çıktığı veri yapısı"),
    ("Önleme", "Prevention", "Dört koşuldan birini tamamen imkânsız kılmak"),
    ("Process kontrol bloğu", "Process Control Block (PCB)", "İşletim sisteminin process hakkında tuttuğu kayıt"),
    ("Sezgisel kural", "Heuristic", "Garanti vermeyen ama pratikte işe yarayan kural"),
    ("Süreç", "Process", "Çalışmakta olan program"),
    ("Tespit", "Detection", "Oluşmuş deadlock'u bulmak"),
    ("Tut ve bekle", "Hold and wait", "Kaynak tutarken başka kaynak beklemek"),
    ("Bekleme grafı", "Wait-for graph", "Yalnızca process'lerden oluşan sade bekleme grafı"),
    ("Yönlü graf", "Directed graph", "Kenarları oklu olan graf"),
]
story.append(T([["Türkçe", "İngilizce", "Kısa anlam"]] + [list(g) for g in gloss], [0.27, 0.30, 0.43]))

if __name__ == "__main__":
    out = str(Path(__file__).parent / "Deadlock_Guardian_El_Kitabi.pdf")
    Doc(out).multiBuild(story)
    print("ok", out)
