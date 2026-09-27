from src.process import ProcessState
from src.turkish import ablative


class Resource:
    def __init__(self, name: str, total_instances: int = 1, event_log=None):
        self.name = name
        self.total_instances = total_instances
        self.allocation = {}  # {process: tutulan_adet}
        self.waiting_queue = []  # [(process, istenen_adet), ...]
        self.event_log = event_log

    def _log(self, event_type: str, process, amount: int, detail: str = ""):
        if self.event_log is not None:
            self.event_log.log(event_type, process.name, self.name, amount, detail)

    @property
    def allocated_instances(self) -> int:
        return sum(self.allocation.values())

    @property
    def available_instances(self) -> int:
        return self.total_instances - self.allocated_instances

    def acquire(self, process, amount: int = 1) -> bool:
        if amount < 1:
            raise ValueError(f"{process.name}, {ablative(self.name)} en az 1 birim istemeli (istenen: {amount}).")
        if amount > self.total_instances:
            # Hiçbir zaman karşılanamaz: bekletmek sonsuz beklemeye (starvation) yol açardı.
            raise ValueError(
                f"{process.name}, {self.name} kaynağının toplam adedinden ({self.total_instances}) fazla isteyemez "
                f"(istenen: {amount})."
            )
        if amount > self.available_instances:
            process.state = ProcessState.WAITING
            if not any(p is process for p, _ in self.waiting_queue):
                self.waiting_queue.append((process, amount))
            self._log("WAITING", process, amount, f"boşta yalnızca {self.available_instances} var")
            return False

        self.allocation[process] = self.allocation.get(process, 0) + amount
        process.held_resources[self.name] = process.held_resources.get(self.name, 0) + amount
        process.state = ProcessState.READY
        self._log("ACQUIRED", process, amount)
        return True

    def release(self, process, amount: int = 1):
        if amount < 1:
            raise ValueError(f"{process.name}, {ablative(self.name)} en az 1 birim bırakmalı (istenen: {amount}).")
        held = self.allocation.get(process, 0)
        if amount > held:
            raise ValueError(
                f"{process.name}, elinde olandan ({held}) fazla {self.name} bırakamaz (istenen: {amount})."
            )

        self.allocation[process] = held - amount
        if self.allocation[process] == 0:
            del self.allocation[process]

        process.held_resources[self.name] -= amount
        if process.held_resources[self.name] == 0:
            del process.held_resources[self.name]

        self._log("RELEASED", process, amount)
        self._serve_waiting_queue()

    def cancel_wait(self, process):
        """Process'in bu kaynaktaki bekleyen isteğini iptal eder (recovery'de sonlandırma için)."""
        self.waiting_queue = [(p, n) for p, n in self.waiting_queue if p is not process]

    def _serve_waiting_queue(self):
        still_waiting = []
        for waiting_process, wanted_amount in self.waiting_queue:
            if wanted_amount <= self.available_instances:
                self.acquire(waiting_process, wanted_amount)
            else:
                still_waiting.append((waiting_process, wanted_amount))
        self.waiting_queue = still_waiting

    def __repr__(self):
        alloc = {p.name: n for p, n in self.allocation.items()}
        waiting = [(p.name, n) for p, n in self.waiting_queue]
        return (
            f"Resource({self.name}, total={self.total_instances}, "
            f"available={self.available_instances}, allocation={alloc}, waiting={waiting})"
        )
