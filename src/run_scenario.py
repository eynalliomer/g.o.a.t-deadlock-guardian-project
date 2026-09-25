import json
import sys

from src.process import Process
from src.resource import Resource
from src.event_log import EventLog
from src.state_table import print_state_table
from src.html_view import render_step, save_html
from src.detection import analyze
from src.bankers import safety_of, evaluate_acquire, safety_text
from src.scenario_loader import declared_processes


def run_scenario_step_by_step(path: str):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    event_log = EventLog()
    resources = {
        r["name"]: Resource(r["name"], total_instances=r.get("total_instances", 1), event_log=event_log)
        for r in data["resources"]
    }
    processes = declared_processes(data)  # Max bildirenler baştan sistemde
    report = analyze(list(resources.values()))
    safety = safety_of(list(processes.values()), list(resources.values()))
    steps_html = [render_step("0. Başlangıç", list(processes.values()), list(resources.values()), report, safety)]
    unsafe_steps = []  # sistemi güvensiz duruma sokan isteklerin başlıkları

    def get_process(name: str) -> Process:
        if name not in processes:
            processes[name] = Process(name)
        return processes[name]

    for i, event in enumerate(data["events"], start=1):
        process = get_process(event["process"])
        resource = resources[event["resource"]]
        amount = event.get("amount", 1)

        decision = None
        if event["action"] == "acquire":
            # Banker's: isteği gerçekleştirmeden ÖNCE değerlendir (bu hafta yalnızca uyarır, engellemez).
            decision = evaluate_acquire(process, resource, amount, list(processes.values()), list(resources.values()))
            resource.acquire(process, amount)
            title = f"{i}. {process.name}, {resource.name}'den {amount} birim istiyor"
        elif event["action"] == "release":
            resource.release(process, amount)
            title = f"{i}. {process.name}, {resource.name}'den {amount} birim bırakıyor"
        else:
            raise ValueError(f"Bilinmeyen action: {event['action']}")

        report = analyze(list(resources.values()))
        safety = safety_of(list(processes.values()), list(resources.values()))
        if decision is not None and decision.status == "UNSAFE":
            unsafe_steps.append(title)
        steps_html.append(
            render_step(title, list(processes.values()), list(resources.values()), report, safety, decision)
        )

    return {
        "description": data.get("description", ""),
        "processes": processes,
        "resources": resources,
        "event_log": event_log,
        "steps_html": steps_html,
        "report": report,
        "safety": safety,
        "unsafe_steps": unsafe_steps,
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

    out_path = save_html(result["steps_html"])
    print(f"\nGörsel önizleme kaydedildi: {out_path}")


if __name__ == "__main__":
    main()
