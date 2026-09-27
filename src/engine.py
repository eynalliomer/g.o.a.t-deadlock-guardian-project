"""Simülasyon motoru (MVC'deki Model): durumu tutar, eylemleri uygular, analiz eder.

Ekranı bilmez; konsol aracı (run_scenario) ve web arayüzü (app) aynı motoru kullanır.

Durum = başlangıç senaryosu + o ana kadar uygulanan eylemler listesi (event sourcing).
Simülasyon deterministik olduğu için "geri al", son eylem hariç hepsini baştan yeniden oynatmaktır.
"""
import json
from dataclasses import dataclass, field

from src.bankers import evaluate_acquire, safety_of
from src.detection import analyze
from src.event_log import EventLog
from src.process import Process, ProcessState
from src.recovery import apply_option, make_option, recover, recovery_options
from src.resource import Resource
from src.risk import assess_risk
from src.turkish import ablative

ACTIONS = {"acquire", "release", "recover", "terminate", "preempt"}


def declared_processes(data) -> dict:
    """Senaryonun (opsiyonel) processes bölümündeki processleri Max ve öncelikleriyle oluşturur."""
    return {
        p["name"]: Process(p["name"], max_claim=p.get("max"), priority=p.get("priority", 1))
        for p in data.get("processes", [])
    }


@dataclass
class Step:
    """Uygulanmış tek bir eylem ve sonucu."""
    title: str
    action: dict
    from_scenario: bool  # senaryodaki sıradan mı geldi, yoksa kullanıcı mı elle yaptı
    risk: object
    decision: object = None  # Banker's değerlendirmesi (yalnızca acquire'da)
    applied: list = field(default_factory=list)  # uygulanan kurtarma seçenekleri


@dataclass
class Analysis:
    """Anlık durumun bütün analizleri."""
    report: object  # deadlock tespiti
    safety: object  # Banker's (güvenli mi, güvenli sıra) ya da None
    risk: object  # risk seviyesi ve nedenleri
    options: list  # kurtarma seçenekleri (deadlock yoksa boş)


class Simulation:
    def __init__(self, data: dict):
        self.data = data
        self._reset()

    @classmethod
    def from_file(cls, path: str) -> "Simulation":
        with open(path, "r", encoding="utf-8") as f:
            return cls(json.load(f))

    @property
    def description(self) -> str:
        return self.data.get("description", "")

    def _reset(self):
        self.event_log = EventLog()
        self.resources = {
            r["name"]: Resource(r["name"], total_instances=r.get("total_instances", 1), event_log=self.event_log)
            for r in self.data["resources"]
        }
        self.processes = declared_processes(self.data)  # Max bildirenler baştan sistemde
        self.cursor = 0  # senaryoda sıradaki olayın indeksi
        self.history = []  # uygulanan Step'ler
        self.initial_risk = assess_risk(self.process_list, self.resource_list)

    @property
    def process_list(self):
        return list(self.processes.values())

    @property
    def resource_list(self):
        return list(self.resources.values())

    def next_event(self):
        events = self.data["events"]
        return events[self.cursor] if self.cursor < len(events) else None

    def analysis(self) -> Analysis:
        return Analysis(
            report=analyze(self.resource_list),
            safety=safety_of(self.process_list, self.resource_list),
            risk=assess_risk(self.process_list, self.resource_list),
            options=recovery_options(self.process_list, self.resource_list),
        )

    # --- Eylemler ---

    def step(self):
        """Senaryodaki sıradaki olayı uygular; senaryo bittiyse None."""
        event = self.next_event()
        return None if event is None else self._apply(event, from_scenario=True)

    def apply(self, action: dict) -> Step:
        """Senaryo dışında, kullanıcının elle yaptığı bir eylem."""
        return self._apply(action, from_scenario=False)

    def apply_option(self, index: int) -> Step:
        """Anlık kurtarma seçeneklerinden index'inciyi uygular (0 = önerilen)."""
        option = self.analysis().options[index]
        action = {"action": option.kind, "process": option.process.name}
        if option.resource is not None:
            action["resource"] = option.resource.name
        return self.apply(action)

    def undo(self):
        """Son eylemi geri alır: baştan başlayıp son eylem hariç hepsini yeniden oynatır."""
        if not self.history:
            return
        replay = [(s.action, s.from_scenario) for s in self.history[:-1]]
        self._reset()
        for action, from_scenario in replay:
            self._apply(action, from_scenario)

    def _get_process(self, name: str) -> Process:
        if name not in self.processes:
            self.processes[name] = Process(name)
        return self.processes[name]

    def _record(self, option):
        resource_name = option.resource.name if option.resource else "tümü"
        self.event_log.log("RECOVERY", option.process.name, resource_name, option.freed_units,
                           f"{option.label()} (maliyet {option.cost})")

    def _apply(self, action: dict, from_scenario: bool) -> Step:
        kind = action.get("action")
        if kind not in ACTIONS:
            raise ValueError(f"Bilinmeyen action: {kind}")
        n = len(self.history) + 1
        decision = None
        applied = []

        if kind == "recover":
            # Otomatik kurtarma: en ucuz seçeneği uygula, tespiti tekrarla, deadlock bitene kadar.
            applied = recover(self.process_list, self.resource_list, on_apply=self._record)
            title = f"{n}. Recovery: " + ("; ".join(o.label() for o in applied) or "deadlock yok, işlem gerekmedi")
        else:
            # Durumu değiştirmeden önce eylemi doğrula: hatalı eylem sistemi yarım bırakmasın.
            name = action.get("process")
            if not name:
                raise ValueError(f"'{kind}' eyleminde process adı eksik.")
            existing = self.processes.get(name)
            if existing is not None and existing.state == ProcessState.TERMINATED:
                raise ValueError(f"{name} sonlandırıldı, yeni eylem alamaz.")
            if kind != "terminate" and action.get("resource") not in self.resources:
                raise ValueError(f"Bilinmeyen kaynak: {action.get('resource')}")
            if kind in ("acquire", "release") and existing is not None and existing.state == ProcessState.WAITING:
                # Bekleyen process bloke durumdadır (CPU'da çalışmıyor), yeni istek ya da bırakma yapamaz.
                raise ValueError(f"{name} şu an bir kaynağı bekliyor (WAITING); yeni {kind} yapamaz.")
            process = self._get_process(name)
            resource = self.resources.get(action.get("resource"))
            amount = action.get("amount", 1)

            if kind in ("terminate", "preempt"):
                # Elle kurtarma: kurbanı (ve geri almada kaynağı) kullanıcı/senaryo seçer.
                option = make_option(kind, process, resource)
                self._record(option)
                apply_option(option, self.resource_list)
                applied = [option]
                title = f"{n}. Recovery: {option.label()}"
            elif kind == "acquire":
                # Banker's: isteği gerçekleştirmeden ÖNCE değerlendir (yalnızca uyarır, engellemez).
                decision = evaluate_acquire(process, resource, amount, self.process_list, self.resource_list)
                resource.acquire(process, amount)
                title = f"{n}. {process.name}, {ablative(resource.name)} {amount} birim istiyor"
            else:  # release
                resource.release(process, amount)
                title = f"{n}. {process.name}, {ablative(resource.name)} {amount} birim bırakıyor"

        step = Step(title, action, from_scenario, assess_risk(self.process_list, self.resource_list),
                    decision, applied)
        self.history.append(step)
        if from_scenario:
            self.cursor += 1
        return step
