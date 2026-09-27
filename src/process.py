from enum import Enum, auto


class ProcessState(Enum):
    READY = auto()
    WAITING = auto()
    TERMINATED = auto()  # recovery sırasında kurban seçilip sonlandırıldı


class Process:
    def __init__(self, name: str, max_claim: dict | None = None, priority: int = 1):
        self.name = name
        self.state = ProcessState.READY
        self.held_resources = {}  # {kaynak_adı: tutulan_adet}
        self.max_claim = max_claim  # Banker's için baştan bildirilen Max ({kaynak_adı: adet}); None = bildirilmedi
        self.priority = priority  # recovery: yüksek öncelikli process kurban seçilmeye daha pahalıdır
        self.victim_count = 0  # recovery: kaç kez kurban seçildi (starvation'ı önlemek için maliyete eklenir)

    def __repr__(self):
        return f"Process({self.name}, state={self.state.name}, held={self.held_resources})"
