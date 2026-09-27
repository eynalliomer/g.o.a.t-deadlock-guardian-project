"""Web arayüzü (MVC'deki Controller): düğmelerden gelen istekleri motora iletir.

Çalıştırma:  python -m src.app   →  http://127.0.0.1:5050
(5000 değil: macOS'te AirPlay alıcısı 5000 portunu kullanıyor.)
Her düğme bir POST isteği gönderir; eylem uygulanır ve sayfaya geri yönlendirilir
(POST → yönlendir → GET): sayfa yenilenince aynı eylem iki kez uygulanmaz.
"""
import os

from flask import Flask, redirect, request

from src.dashboard_view import render_dashboard
from src.engine import Simulation

SCENARIO_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scenarios")
DEFAULT_SCENARIO = "hafta8_recovery.json"


def list_scenarios() -> list:
    return sorted(f for f in os.listdir(SCENARIO_DIR) if f.endswith(".json"))


def create_app(scenario: str = DEFAULT_SCENARIO) -> Flask:
    app = Flask(__name__)
    # Tek kullanıcılı yerel demo: durum sunucunun belleğinde tutulur.
    state = {"scenario": scenario, "sim": Simulation.from_file(os.path.join(SCENARIO_DIR, scenario)), "error": None}

    def run(action):
        """Eylemi uygular; hata olursa durumu bozmadan mesajı bir sonraki sayfada gösterir."""
        try:
            action()
        except (ValueError, KeyError, IndexError) as e:
            state["error"] = str(e)
        return redirect("/")

    @app.get("/")
    def dashboard():
        error, state["error"] = state["error"], None  # hata mesajı yalnızca bir kez gösterilir
        return render_dashboard(state["sim"], state["scenario"], list_scenarios(), error)

    @app.post("/load")
    def load():
        def action():
            name = request.form.get("scenario", "")
            if name not in list_scenarios():  # yalnızca scenarios/ klasöründeki dosyalar
                raise ValueError(f"Senaryo bulunamadı: {name}")
            state["sim"] = Simulation.from_file(os.path.join(SCENARIO_DIR, name))
            state["scenario"] = name
        return run(action)

    @app.post("/step")
    def step():
        return run(lambda: state["sim"].step())

    @app.post("/undo")
    def undo():
        return run(lambda: state["sim"].undo())

    @app.post("/reset")
    def reset():
        return run(lambda: state.update(sim=Simulation(state["sim"].data)))

    @app.post("/option/<int:index>")
    def option(index):
        return run(lambda: state["sim"].apply_option(index))

    @app.post("/action")
    def manual_action():
        def action():
            sim = state["sim"]
            process, resource = request.form["process"], request.form["resource"]
            if process not in sim.processes or resource not in sim.resources:
                raise ValueError("Geçersiz process ya da kaynak.")
            amount = int(request.form.get("amount", 1))
            if amount < 1:
                raise ValueError("Birim sayısı en az 1 olmalı.")
            sim.apply({"action": request.form["action"], "process": process, "resource": resource,
                       "amount": amount})
        return run(action)

    return app


if __name__ == "__main__":
    create_app().run(host="127.0.0.1", port=5050, debug=False)
