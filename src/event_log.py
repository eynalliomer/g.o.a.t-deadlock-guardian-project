class EventLog:
    def __init__(self):
        self.events = []

    def log(self, event_type: str, process_name: str, resource_name: str, amount: int, detail: str = ""):
        self.events.append({
            "step": len(self.events) + 1,
            "type": event_type,
            "process": process_name,
            "resource": resource_name,
            "amount": amount,
            "detail": detail,
        })

    def print_all(self):
        for event in self.events:
            print(
                f"[{event['step']:>2}] {event['type']:<9} "
                f"{event['process']} x {event['resource']}({event['amount']}) {event['detail']}"
            )

    def __repr__(self):
        return f"EventLog({len(self.events)} olay)"
