"""Web dashboard'u (MVC'deki View): motorun anlık durumunu tek sayfada çizer.

Kart ve graf çizimi statik önizlemeyle (html_view, graph_view) ortaktır.
Düğmeler form olarak app.py'deki adreslere POST eder.
"""
from src.bankers import safety_text
from src.graph_view import render_rag_svg
from src.html_view import RISK_COLORS, process_card, resource_card
from src.process import ProcessState


def describe_event(event) -> str:
    kind = event["action"]
    if kind == "recover":
        return "Recovery (otomatik, en ucuz seçenek)"
    if kind == "terminate":
        return f"Sonlandır: {event['process']}"
    if kind == "preempt":
        return f"Geri al: {event['resource']}, sahibi {event['process']}"
    verb = "istiyor" if kind == "acquire" else "bırakıyor"
    return f"{event['process']}, {event['resource']}'den {event.get('amount', 1)} birim {verb}"


def _button(path, label, disabled=False, css=""):
    attr = " disabled" if disabled else ""
    return f'<form method="post" action="{path}"><button class="{css}"{attr}>{label}</button></form>'


def _header(scenario, scenarios):
    options = "".join(
        f'<option value="{name}"{" selected" if name == scenario else ""}>{name}</option>' for name in scenarios
    )
    return f"""
    <header>
        <h1>🛡 Deadlock Guardian</h1>
        <form method="post" action="/load" class="load">
            <select name="scenario">{options}</select>
            <button>Senaryoyu yükle</button>
        </form>
    </header>
    """


def _controls(sim):
    total = len(sim.data["events"])
    upcoming = sim.next_event()
    upcoming_text = f"Sıradaki: {describe_event(upcoming)}" if upcoming else "Senaryo bitti"
    timeline = [sim.initial_risk] + [s.risk for s in sim.history]
    chips = "".join(
        f'<span class="chip" style="background:{RISK_COLORS[r.level.name]}" title="{r.level.name}">{i}</span>'
        for i, r in enumerate(timeline)
    )
    return f"""
    <div class="controls">
        {_button("/reset", "⟲ Sıfırla")}
        {_button("/undo", "◀ Geri al", disabled=not sim.history)}
        {_button("/step", "Sonraki olay ▶", disabled=upcoming is None, css="primary")}
        <span class="progress"><b>Olay {sim.cursor} / {total}</b> · {upcoming_text}</span>
    </div>
    <div class="timeline"><b>Risk seyri:</b> {chips}</div>
    """


def _summary(sim, analysis):
    active = [p for p in sim.process_list if p.state != ProcessState.TERMINATED]
    free = sum(r.available_instances for r in sim.resource_list)
    total = sum(r.total_instances for r in sim.resource_list)
    level = analysis.risk.level.name
    deadlock = "VAR" if analysis.report.has_deadlock else "yok"
    return f"""
    <div class="summary">
        <div class="stat"><span>Aktif process</span><b>{len(active)}</b></div>
        <div class="stat"><span>Kaynak (boş / toplam birim)</span><b>{free} / {total}</b></div>
        <div class="stat"><span>Deadlock</span><b>{deadlock}</b></div>
        <div class="stat" style="border-color:{RISK_COLORS[level]}"><span>Risk</span>
            <b style="color:{RISK_COLORS[level]}">{level}</b></div>
    </div>
    """


def _status_panel(sim, analysis):
    """Risk, deadlock ve Banker's bilgisinin tek panelde birleşimi."""
    level = analysis.risk.level.name
    reasons = "".join(f"<li>{r}</li>" for r in analysis.risk.reasons)
    last = sim.history[-1] if sim.history else None
    warning = ""
    if last is not None and last.decision is not None and last.decision.status == "UNSAFE":
        warning = '<p class="warn">⚠ Son istek sistemi güvensiz duruma soktu (Banker\'s bu isteği onaylamazdı).</p>'
    return f"""
    <section class="panel" style="border-left-color:{RISK_COLORS[level]}">
        <h2>Durum <span class="risk-badge" style="background:{RISK_COLORS[level]}">RİSK: {level}</span></h2>
        <ul>{reasons}</ul>
        {warning}
        <p class="muted">🏦 {safety_text(analysis.safety)}</p>
        {f'<p class="muted">Son eylem: {last.title}</p>' if last else ''}
    </section>
    """


def _recovery_panel(analysis):
    if not analysis.options:
        return ""
    rows = "".join(
        f'<tr class="{"best" if i == 0 else ""}"><td>{o.label()}</td><td>{o.cost}</td>'
        f'<td>{_button(f"/option/{i}", "✅ Uygula (önerilen)" if i == 0 else "Uygula")}</td></tr>'
        for i, o in enumerate(analysis.options)
    )
    return f"""
    <section class="panel recovery-panel">
        <h2>🛠 Kurtarma seçenekleri</h2>
        <p class="muted">maliyet = öncelik×10 − serbest bırakılan birim×2 + kurban sayısı×5</p>
        <table><tr><th>Seçenek</th><th>Maliyet</th><th></th></tr>{rows}</table>
    </section>
    """


def _manual_panel(sim):
    active = [p.name for p in sim.process_list if p.state != ProcessState.TERMINATED]
    p_opts = "".join(f"<option>{name}</option>" for name in active)
    r_opts = "".join(f"<option>{name}</option>" for name in sim.resources)
    return f"""
    <section class="panel">
        <h2>✋ Elle eylem</h2>
        <form method="post" action="/action" class="manual">
            <select name="process">{p_opts}</select>
            <select name="resource">{r_opts}</select>
            <input type="number" name="amount" value="1" min="1">
            <button name="action" value="acquire">İste</button>
            <button name="action" value="release">Bırak</button>
        </form>
        <p class="muted">Senaryo dışı bir eylem; "Geri al" ile geri alınabilir.</p>
    </section>
    """


def _event_log(sim):
    rows = "".join(
        f"<tr><td>{e['step']}</td><td>{e['type']}</td><td>{e['process']}</td>"
        f"<td>{e['resource']}</td><td>{e['amount']}</td><td>{e['detail']}</td></tr>"
        for e in reversed(sim.event_log.events)
    ) or '<tr><td colspan="6" class="muted">Henüz olay yok.</td></tr>'
    return f"""
    <section class="panel">
        <h2>📜 Olay akışı</h2>
        <div class="log"><table>
            <tr><th>#</th><th>Tür</th><th>Process</th><th>Kaynak</th><th>Birim</th><th>Ayrıntı</th></tr>{rows}
        </table></div>
    </section>
    """


def render_dashboard(sim, scenario, scenarios, error=None) -> str:
    analysis = sim.analysis()
    deadlocked = set(analysis.report.deadlocked)
    cards = "".join(process_card(p, p.name in deadlocked) for p in sim.process_list)
    cards += "".join(resource_card(r) for r in sim.resource_list)
    error_html = f'<div class="error">⚠ {error}</div>' if error else ""
    return f"""<!doctype html>
<html lang="tr"><head><meta charset="utf-8"><title>Deadlock Guardian</title>{STYLE}</head>
<body>
    {_header(scenario, scenarios)}
    <p class="muted description">{sim.description}</p>
    {error_html}
    {_controls(sim)}
    {_summary(sim, analysis)}
    <div class="grid">
        <div class="col">
            {_status_panel(sim, analysis)}
            {_recovery_panel(analysis)}
            {_manual_panel(sim)}
        </div>
        <div class="col">
            <section class="panel"><h2>🕸 Resource Allocation Graph</h2>
                <div class="graph">{render_rag_svg(sim.process_list, sim.resource_list, analysis.report)}</div>
            </section>
            <section class="panel"><h2>Processler ve kaynaklar</h2><div class="row">{cards}</div></section>
        </div>
    </div>
    {_event_log(sim)}
</body></html>"""


STYLE = """
<style>
    body { font-family: sans-serif; background:#f4f4f4; margin:0; padding:16px 24px; }
    header { display:flex; align-items:center; gap:20px; flex-wrap:wrap; }
    header h1 { margin:0; font-size:24px; }
    form { display:inline; margin:0; }
    button, select, input { font-size:14px; padding:6px 12px; border-radius:6px; border:1px solid #999;
                            background:white; }
    button { cursor:pointer; }
    button:disabled { opacity:0.4; cursor:default; }
    button.primary { background:#2c3e50; color:white; border-color:#2c3e50; }
    input[type=number] { width:60px; }
    .description { margin:6px 0 12px; }
    .muted { color:#777; font-size:13px; }
    .error { background:#fdedec; color:#c0392b; border:1px solid #e6b0aa; padding:8px 12px;
             border-radius:6px; margin-bottom:10px; font-weight:bold; }
    .controls { display:flex; gap:8px; align-items:center; flex-wrap:wrap; margin-bottom:8px; }
    .progress { margin-left:8px; }
    .timeline { display:flex; gap:6px; align-items:center; flex-wrap:wrap; margin-bottom:12px; }
    .chip { color:white; font-weight:bold; font-size:12px; width:24px; height:24px; line-height:24px;
            text-align:center; border-radius:50%; }
    .summary { display:grid; grid-template-columns:repeat(auto-fit, minmax(160px, 1fr)); gap:12px;
               margin-bottom:14px; }
    .stat { background:white; border:1px solid #ddd; border-top:4px solid #3498db; border-radius:8px;
            padding:10px 14px; }
    .stat span { display:block; color:#777; font-size:13px; }
    .stat b { font-size:24px; }
    .grid { display:grid; grid-template-columns:minmax(320px, 1fr) minmax(320px, 1.3fr); gap:14px; }
    @media (max-width: 900px) { .grid { grid-template-columns:1fr; } }
    .panel { background:white; border:1px solid #ddd; border-left:6px solid #3498db; border-radius:8px;
             padding:10px 14px; margin-bottom:14px; }
    .panel h2 { font-size:17px; margin:0 0 8px; }
    .panel ul { margin:4px 0; padding-left:20px; }
    .recovery-panel { border-left-color:#8e44ad; }
    .risk-badge { color:white; font-size:13px; padding:3px 10px; border-radius:4px; margin-left:8px; }
    .warn { color:#c0392b; font-weight:bold; margin:6px 0; }
    table { border-collapse:collapse; width:100%; }
    td, th { padding:4px 8px; text-align:left; border-bottom:1px solid #eee; font-size:14px; }
    tr.best { background:#e8f8ef; font-weight:bold; }
    .graph { overflow-x:auto; }
    .row { display:flex; gap:10px; flex-wrap:wrap; }
    .card { border:2px solid #ccc; border-radius:8px; padding:6px 12px; background:white; min-width:150px;
            font-size:13px; }
    .card h3 { margin:4px 0; font-size:15px; }
    .card p { margin:4px 0; }
    .card.deadlocked { background:#fdedec; box-shadow:0 0 0 3px #c0392b; }
    .card.terminated { opacity:0.55; background:#ecf0f1; }
    .badge { background:#c0392b; color:white; font-size:11px; padding:2px 6px; border-radius:4px; }
    .log { max-height:260px; overflow-y:auto; }
</style>
"""
