from src.process import ProcessState


class Resource:
    def __init__(self, name: str):
        self.name = name
        self.owner = None
        self.waiting_queue = []

    @property
    def is_free(self) -> bool:
        return self.owner is None

    def acquire(self, process) -> bool:
        if self.is_free:
            self.owner = process
            process.state = ProcessState.READY
            process.held_resources.append(self.name)
            return True

        process.state = ProcessState.WAITING
        if process not in self.waiting_queue:
            self.waiting_queue.append(process)
        return False

    def release(self, process):
        if self.owner is not process:
            raise ValueError(
                f"{process.name} bu kaynağın ({self.name}) sahibi değil, bırakamaz."
            )

        self.owner = None
        process.held_resources.remove(self.name)

        if self.waiting_queue:
            next_process = self.waiting_queue.pop(0)
            self.acquire(next_process)

    def __repr__(self):
        owner_name = self.owner.name if self.owner else None
        waiting_names = [p.name for p in self.waiting_queue]
        return f"Resource({self.name}, owner={owner_name}, waiting={waiting_names})"
