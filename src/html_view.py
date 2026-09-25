from src.process import ProcessState
from src.graph_view import render_rag_svg


def _process_card(process, deadlocked=False):
    color = "#2ecc71" if process.state == ProcessState.READY else "#e74c3c"
    badge = '<span class="badge">DEADLOCK</span>' if deadlocked else ""
    extra_class = " deadlocked" if deadlocked else ""
    if process.held_resources:
        held = ", ".join(f"{name}×{amount}" for name, amount in process.held_resources.items())
    else:
        held = "—"
    return f"""
    <div class="card{extra_class}" style="border-color:{color}">
        <h3>{process.name} {badge}</h3>
        <p><b>Durum:</b> <span style="color:{color}">{process.state.name}</span></p>
        <p><b>Elindeki kaynaklar:</b> {held}</p>
    </div>
    """


def _resource_card(resource):
    allocation = ", ".join(
        f"{p.name}×{amount}" for p, amount in resource.allocation.items()
    ) or "—"
    waiting = ", ".join(
        f"{p.name}(ister {amount})" for p, amount in resource.waiting_queue
    ) or "—"
    return f"""
    <div class="card" style="border-color:#3498db">
        <h3>{resource.name} ({resource.available_instances}/{resource.total_instances} boşta)</h3>
        <p><b>Dağıtım:</b> {allocation}</p>
        <p><b>Bekleyen kuyruk:</b> {waiting}</p>
    </div>
    """


def _report_banner(report):
    if report is None:
        return ""
    if report.has_deadlock:
        level = "danger"
    elif report.cycle:
        level = "warning"
    else:
        level = "ok"
    return f'<div class="banner {level}">{report.summary()}</div>'


def render_step(title: str, processes, resources, report=None) -> str:
    deadlocked = set(report.deadlocked) if report else set()
    process_cards = "".join(_process_card(p, p.name in deadlocked) for p in processes)
    resource_cards = "".join(_resource_card(r) for r in resources)
    return f"""
    <section class="step">
        <h2>{title}</h2>
        {_report_banner(report)}
        <div class="step-body">
            <div class="row cards">{process_cards}{resource_cards}</div>
            <div class="graph">{render_rag_svg(processes, resources, report)}</div>
        </div>
    </section>
    """


def save_html(steps_html: list[str], out_path: str = "simulation_view.html"):
    style = """
    <style>
        body { font-family: sans-serif; background:#f4f4f4; padding:20px; }
        .step { margin-bottom: 30px; }
        .row { display:flex; gap:16px; flex-wrap:wrap; }
        .card { border:2px solid #ccc; border-radius:8px; padding:12px 16px;
                background:white; min-width:160px; }
        h2 { border-bottom:2px solid #333; padding-bottom:4px; }
        .banner { padding:8px 12px; border-radius:6px; margin-bottom:12px; font-weight:bold; }
        .banner.ok { background:#e8f8ef; color:#1e8449; }
        .banner.warning { background:#fef5e7; color:#b9770e; }
        .banner.danger { background:#fdedec; color:#c0392b; }
        .card.deadlocked { background:#fdedec; box-shadow:0 0 0 3px #c0392b; }
        .step-body { display:flex; gap:20px; align-items:flex-start; flex-wrap:wrap; }
        .cards { flex:1; min-width:300px; }
        .graph { background:white; border-radius:8px; padding:8px; border:1px solid #ddd; }
        .badge { background:#c0392b; color:white; font-size:11px; padding:2px 6px;
                 border-radius:4px; vertical-align:middle; }
        .nav { position:sticky; top:0; z-index:1; display:flex; gap:10px; align-items:center;
               background:#f4f4f4; padding:10px 0; margin-bottom:10px; border-bottom:1px solid #ddd; }
        .nav button { font-size:15px; padding:6px 14px; border-radius:6px; border:1px solid #999;
                      background:white; cursor:pointer; }
        .nav button:disabled { opacity:0.4; cursor:default; }
        #counter { font-weight:bold; min-width:110px; text-align:center; }
        .hint { color:#777; font-size:13px; margin-left:auto; }
    </style>
    """
    nav = """
    <div class="nav">
        <button id="prev">◀ Önceki</button>
        <span id="counter"></span>
        <button id="next">Sonraki ▶</button>
        <button id="toggle-all">Tümünü göster</button>
        <span class="hint">Klavye: ← →</span>
    </div>
    """
    # JS yalnızca adımları gizleyip gösteriyor; JS kapalıysa bütün adımlar alt alta görünür.
    script = """
    <script>
        const steps = document.querySelectorAll(".step");
        const prev = document.getElementById("prev");
        const next = document.getElementById("next");
        const toggle = document.getElementById("toggle-all");
        const counter = document.getElementById("counter");
        let current = 0;
        let showAll = false;

        function update() {
            steps.forEach((step, i) => {
                step.style.display = (showAll || i === current) ? "" : "none";
            });
            counter.textContent = showAll ? "Tüm adımlar" : `Adım ${current + 1} / ${steps.length}`;
            prev.disabled = showAll || current === 0;
            next.disabled = showAll || current === steps.length - 1;
            toggle.textContent = showAll ? "Adım adım göster" : "Tümünü göster";
        }

        function go(delta) {
            if (showAll) return;
            current = Math.min(Math.max(current + delta, 0), steps.length - 1);
            update();
        }

        prev.addEventListener("click", () => go(-1));
        next.addEventListener("click", () => go(1));
        toggle.addEventListener("click", () => { showAll = !showAll; update(); });
        document.addEventListener("keydown", (e) => {
            if (e.key === "ArrowRight") go(1);
            if (e.key === "ArrowLeft") go(-1);
        });
        update();
    </script>
    """
    html = (f"<html><head><meta charset='utf-8'>{style}</head>"
            f"<body>{nav}{''.join(steps_html)}{script}</body></html>")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    return out_path
