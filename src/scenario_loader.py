from src.engine import Simulation


def load_scenario(path: str):
    """Senaryoyu baştan sona çalıştırır ve son durumu döner (adım adım görünüm gerekmeyen kullanım için)."""
    sim = Simulation.from_file(path)
    while sim.step() is not None:
        pass
    return {
        "description": sim.description,
        "processes": sim.processes,
        "resources": sim.resources,
        "event_log": sim.event_log,
    }
