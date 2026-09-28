"""Final raporu ve sunum için dashboard ekran görüntülerini üretir.

Sunucu gerekmez: motor (Simulation) istenen adıma kadar oynatılır, dashboard HTML'i
geçici bir dosyaya yazılır ve Chrome'un başsız (headless) moduyla PNG'ye çevrilir.

    python 04-Kaynaklar/ekran_goruntusu_al.py
"""
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.app import list_scenarios  # noqa: E402
from src.dashboard_view import render_dashboard  # noqa: E402
from src.engine import Simulation  # noqa: E402

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
OUT = Path(__file__).parent / "rapor_gorselleri"

# (dosya adı, senaryo, kaç olay oynatılacak, pencere yüksekliği)
SHOTS = [
    ("01_low", "final_demo.json", 2, 1000),
    ("02_medium", "final_demo.json", 3, 1000),
    ("03_high", "final_demo.json", 4, 1000),
    ("04_critical", "final_demo.json", 6, 1000),
    ("05_recovery", "final_demo.json", 7, 1000),
    ("06_coklu_deadlock", "hafta10_coklu_deadlock.json", 8, 1000),
]


def shoot(name, scenario, steps, height):
    sim = Simulation.from_file(str(ROOT / "scenarios" / scenario))
    for _ in range(steps):
        sim.step()
    html = render_dashboard(sim, scenario, list_scenarios())
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as f:
        f.write(html)
    out = OUT / f"{name}.png"
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                    f"--screenshot={out}", f"--window-size=1400,{height}", f"file://{f.name}"],
                   check=True, capture_output=True)
    Path(f.name).unlink()
    print("ok", out.name)


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    for shot in SHOTS:
        shoot(*shot)
