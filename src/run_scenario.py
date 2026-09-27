import sys

from src.state_table import print_state_table
from src.html_view import render_step, save_html
from src.bankers import safety_text
from src.engine import Simulation


def run_scenario_step_by_step(path: str):
    """Senaryoyu baştan sona motorla oynatır ve her adım için HTML üretir (statik önizleme)."""
    sim = Simulation.from_file(path)

    def render(title, step=None):
        a = sim.analysis()
        return render_step(title, sim.process_list, sim.resource_list, a.report, a.safety,
                           step.decision if step else None, a.risk,
                           options=a.options, applied=step.applied if step else None)

    steps_html = [render("0. Başlangıç")]
    while (step := sim.step()) is not None:
        steps_html.append(render(step.title, step))

    final = sim.analysis()
    return {
        "description": sim.description,
        "processes": sim.processes,
        "resources": sim.resources,
        "event_log": sim.event_log,
        "steps_html": steps_html,
        "report": final.report,
        "safety": final.safety,
        "unsafe_steps": [s.title for s in sim.history if s.decision is not None and s.decision.status == "UNSAFE"],
        "risk_timeline": [sim.initial_risk] + [s.risk for s in sim.history],
    }


def main():
    if len(sys.argv) != 2:
        print("Kullanım: python -m src.run_scenario scenarios/<dosya>.json")
        sys.exit(1)

    path = sys.argv[1]
    result = run_scenario_step_by_step(path)

    print(f"Senaryo: {result['description']}")

    print("\n--- Olay Kaydı ---")
    result["event_log"].print_all()

    print_state_table(result["processes"], result["resources"])

    print("\n--- Deadlock Analizi ---")
    print(result["report"].summary())

    print("\n--- Banker's Analizi ---")
    print(safety_text(result["safety"]))
    for title in result["unsafe_steps"]:
        print(f"⚠ Sistemi güvensiz duruma sokan istek: {title}")

    print("\n--- Risk Seyri ---")
    print(" → ".join(risk.level.name for risk in result["risk_timeline"]))
    final = result["risk_timeline"][-1]
    print(f"Son durum: {final.level.name}")
    for reason in final.reasons:
        print(f"  • {reason}")

    out_path = save_html(result["steps_html"], result["risk_timeline"])
    print(f"\nGörsel önizleme kaydedildi: {out_path}")


if __name__ == "__main__":
    main()
