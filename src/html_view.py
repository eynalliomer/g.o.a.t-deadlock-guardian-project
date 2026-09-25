from src.process import ProcessState


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
        <div class="row">{process_cards}{resource_cards}</div>
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
        .badge { background:#c0392b; color:white; font-size:11px; padding:2px 6px;
                 border-radius:4px; vertical-align:middle; }
    </style>
    """
    html = f"<html><head><meta charset='utf-8'>{style}</head><body>{''.join(steps_html)}</body></html>"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    return out_path
