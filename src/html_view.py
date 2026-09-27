from src.process import ProcessState
from src.graph_view import render_rag_svg
from src.bankers import safety_text


def _claim_lines(process):
    """Banker's için: Max ve Need = Max − Allocation (Max bildirilmemişse boş)."""
    if process.max_claim is None:
        return ""
    fmt = lambda d: ", ".join(f"{r}×{n}" for r, n in d.items() if n) or "—"
    need = {r: n - process.held_resources.get(r, 0) for r, n in process.max_claim.items()}
    return f"<p><b>Max:</b> {fmt(process.max_claim)} · <b>Need:</b> {fmt(need)}</p>"


def _process_card(process, deadlocked=False):
    color = {ProcessState.READY: "#2ecc71", ProcessState.WAITING: "#e74c3c",
             ProcessState.TERMINATED: "#95a5a6"}[process.state]
    badge = '<span class="badge">DEADLOCK</span>' if deadlocked else ""
    extra_class = " deadlocked" if deadlocked else ""
    if process.state == ProcessState.TERMINATED:
        extra_class = " terminated"
    if process.held_resources:
        held = ", ".join(f"{name}×{amount}" for name, amount in process.held_resources.items())
    else:
        held = "—"
    return f"""
    <div class="card{extra_class}" style="border-color:{color}">
        <h3>{process.name} {badge}</h3>
        <p><b>Durum:</b> <span style="color:{color}">{process.state.name}</span></p>
        <p><b>Elindeki kaynaklar:</b> {held}</p>
        {_claim_lines(process)}
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


def _safety_banner(safety, decision):
    if safety is None:
        return ""
    level = "ok" if safety[0] else "warning"
    html = f'<div class="banner {level}">🏦 {safety_text(safety)}</div>'
    if decision is not None and decision.status == "UNSAFE":
        html += '<div class="banner danger">⚠ Bu istek sistemi güvensiz duruma soktu (Banker\'s bu isteği onaylamazdı).</div>'
    return html


RISK_COLORS = {"LOW": "#27ae60", "MEDIUM": "#c9a000", "HIGH": "#e67e22", "CRITICAL": "#c0392b"}


def _risk_panel(risk):
    if risk is None:
        return ""
    name = risk.level.name
    reasons = "".join(f"<li>{reason}</li>" for reason in risk.reasons)
    return f"""
    <div class="risk" style="border-color:{RISK_COLORS[name]}">
        <span class="risk-badge" style="background:{RISK_COLORS[name]}">RİSK: {name}</span>
        <ul>{reasons}</ul>
    </div>
    """


def _risk_timeline(risk_timeline):
    """Sayfanın üstündeki risk seyri: her adım için tıklanabilir renkli bir kutucuk."""
    if not risk_timeline:
        return ""
    chips = "".join(
        f'<span class="chip" data-step="{i}" style="background:{RISK_COLORS[r.level.name]}" '
        f'title="Adım {i}: {r.level.name}">{i}</span>'
        for i, r in enumerate(risk_timeline)
    )
    return f'<div class="timeline"><b>Risk seyri:</b> {chips}</div>'


def _recovery_panel(options, applied):
    """Deadlock varken kurtarma seçenekleri (en ucuzu önerilen); bu adımda uygulanan kurtarma."""
    html = ""
    if applied:
        items = "".join(f"<li>{o.label()} (maliyet {o.cost})</li>" for o in applied)
        html += f'<div class="recovery applied"><b>🛠 Uygulanan kurtarma:</b><ul>{items}</ul></div>'
    if options:
        rows = "".join(
            f'<tr class="{"best" if i == 0 else ""}"><td>{o.label()}</td><td>{o.cost}</td>'
            f'<td>{"✅ önerilen" if i == 0 else ""}</td></tr>'
            for i, o in enumerate(options)
        )
        html += f"""
        <div class="recovery">
            <b>🛠 Kurtarma seçenekleri</b>
            <span class="formula">maliyet = öncelik×10 − serbest bırakılan birim×2 + kurban sayısı×5</span>
            <table><tr><th>Seçenek</th><th>Maliyet</th><th></th></tr>{rows}</table>
        </div>
        """
    return html


def render_step(title: str, processes, resources, report=None, safety=None, decision=None, risk=None,
                options=None, applied=None) -> str:
    deadlocked = set(report.deadlocked) if report else set()
    process_cards = "".join(_process_card(p, p.name in deadlocked) for p in processes)
    resource_cards = "".join(_resource_card(r) for r in resources)
    return f"""
    <section class="step">
        <h2>{title}</h2>
        {_risk_panel(risk)}
        {_report_banner(report)}
        {_safety_banner(safety, decision)}
        {_recovery_panel(options, applied)}
        <div class="step-body">
            <div class="row cards">{process_cards}{resource_cards}</div>
            <div class="graph">{render_rag_svg(processes, resources, report)}</div>
        </div>
    </section>
    """


def save_html(steps_html: list[str], risk_timeline=None, out_path: str = "simulation_view.html"):
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
        .risk { border-left:6px solid; background:white; border-radius:6px; padding:8px 12px; margin-bottom:10px; }
        .risk ul { margin:6px 0 0 0; padding-left:20px; }
        .risk-badge { color:white; font-weight:bold; padding:3px 10px; border-radius:4px; }
        .card.terminated { opacity:0.55; background:#ecf0f1; }
        .recovery { background:white; border:1px solid #ddd; border-left:6px solid #8e44ad;
                    border-radius:6px; padding:8px 12px; margin-bottom:10px; }
        .recovery.applied { border-left-color:#27ae60; }
        .recovery ul { margin:6px 0 0 0; padding-left:20px; }
        .recovery table { border-collapse:collapse; margin-top:6px; }
        .recovery td, .recovery th { padding:3px 12px; text-align:left; border-bottom:1px solid #eee; }
        .recovery tr.best { background:#e8f8ef; font-weight:bold; }
        .formula { color:#777; font-size:12px; margin-left:10px; }
        .timeline { display:flex; gap:6px; align-items:center; margin-bottom:10px; flex-wrap:wrap; }
        .chip { color:white; font-weight:bold; font-size:12px; width:26px; height:26px; line-height:26px;
                text-align:center; border-radius:50%; cursor:pointer; }
        .chip.active { outline:3px solid #333; outline-offset:1px; }
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
    """ + _risk_timeline(risk_timeline)
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
            document.querySelectorAll(".chip").forEach((chip) => {
                chip.classList.toggle("active", !showAll && Number(chip.dataset.step) === current);
            });
        }

        function go(delta) {
            if (showAll) return;
            current = Math.min(Math.max(current + delta, 0), steps.length - 1);
            update();
        }

        prev.addEventListener("click", () => go(-1));
        next.addEventListener("click", () => go(1));
        toggle.addEventListener("click", () => { showAll = !showAll; update(); });
        document.querySelectorAll(".chip").forEach((chip) => {
            chip.addEventListener("click", () => { showAll = false; current = Number(chip.dataset.step); update(); });
        });
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
