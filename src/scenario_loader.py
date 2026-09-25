import json

from src.process import Process
from src.resource import Resource
from src.event_log import EventLog


def declared_processes(data) -> dict:
    """Senaryonun (opsiyonel) processes bölümündeki processleri Max bildirimleriyle oluşturur."""
    return {
        p["name"]: Process(p["name"], max_claim=p.get("max"))
        for p in data.get("processes", [])
    }


def load_scenario(path: str):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    event_log = EventLog()
    resources = {
        r["name"]: Resource(r["name"], total_instances=r.get("total_instances", 1), event_log=event_log)
        for r in data["resources"]
    }
    processes = declared_processes(data)

    def get_process(name: str) -> Process:
        if name not in processes:
            processes[name] = Process(name)
        return processes[name]

    for event in data["events"]:
        process = get_process(event["process"])
        resource = resources[event["resource"]]
        amount = event.get("amount", 1)

        if event["action"] == "acquire":
            resource.acquire(process, amount)
        elif event["action"] == "release":
            resource.release(process, amount)
        else:
            raise ValueError(f"Bilinmeyen action: {event['action']}")

    return {
        "description": data.get("description", ""),
        "processes": processes,
        "resources": resources,
        "event_log": event_log,
    }
