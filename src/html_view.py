from src.process import ProcessState


def _process_card(process):
    color = "#2ecc71" if process.state == ProcessState.READY else "#e74c3c"
    held = ", ".join(process.held_resources) if process.held_resources else "—"
    return f"""
    <div class="card" style="border-color:{color}">
        <h3>{process.name}</h3>
        <p><b>Durum:</b> <span style="color:{color}">{process.state.name}</span></p>
        <p><b>Elindeki kaynaklar:</b> {held}</p>
    </div>
    """


def _resource_card(resource):
    owner = resource.owner.name if resource.owner else "—"
    waiting = ", ".join(p.name for p in resource.waiting_queue) or "—"
    return f"""
    <div class="card" style="border-color:#3498db">
        <h3>{resource.name}</h3>
        <p><b>Sahibi:</b> {owner}</p>
        <p><b>Bekleyen kuyruk:</b> {waiting}</p>
    </div>
    """


def render_step(title: str, processes, resources) -> str:
    process_cards = "".join(_process_card(p) for p in processes)
    resource_cards = "".join(_resource_card(r) for r in resources)
    return f"""
    <section class="step">
        <h2>{title}</h2>
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
    </style>
    """
    html = f"<html><head><meta charset='utf-8'>{style}</head><body>{''.join(steps_html)}</body></html>"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    return out_path
