from enum import Enum, auto


class ProcessState(Enum):
    READY = auto()
    WAITING = auto()


class Process:
    def __init__(self, name: str):
        self.name = name
        self.state = ProcessState.READY
        self.held_resources = []

    def __repr__(self):
        return f"Process({self.name}, state={self.state.name}, held={self.held_resources})"
