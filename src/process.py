from enum import Enum, auto


class ProcessState(Enum):
    READY = auto()
    WAITING = auto()


class Process:
    def __init__(self, name: str, max_claim: dict | None = None):
        self.name = name
        self.state = ProcessState.READY
        self.held_resources = {}  # {kaynak_adı: tutulan_adet}
        self.max_claim = max_claim  # Banker's için baştan bildirilen Max ({kaynak_adı: adet}); None = bildirilmedi

    def __repr__(self):
        return f"Process({self.name}, state={self.state.name}, held={self.held_resources})"
