"""Hafta 10: komut satırı araçları için duman testleri (çöküyor mu, beklenen bölümleri yazıyor mu?)."""
import os
import sys

import pytest

from src import run_scenario, simulation

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_run_scenario_konsol_ciktisi_ve_html(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)  # simulation_view.html geçici klasöre yazılsın
    monkeypatch.setattr(sys, "argv", ["run_scenario", os.path.join(ROOT, "scenarios/hafta8_recovery.json")])
    run_scenario.main()
    out = capsys.readouterr().out
    for section in ["Olay Kaydı", "Process Tablosu", "Deadlock Analizi", "Banker's Analizi", "Risk Seyri"]:
        assert section in out
    assert (tmp_path / "simulation_view.html").exists()


def test_run_scenario_argumansiz_kullanim_mesaji(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["run_scenario"])
    with pytest.raises(SystemExit):
        run_scenario.main()
    assert "Kullanım" in capsys.readouterr().out


def test_hafta2_demo_betigi_calisir(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    simulation.main()
    assert "Başlangıç" in capsys.readouterr().out


# --- Kapsam ölçümünün gösterdiği test edilmemiş dallar ---

def _client(scenario):
    from src.app import create_app
    app = create_app(scenario)
    app.config["TESTING"] = True
    return app.test_client()


def test_web_gecersiz_process_adi_reddedilir():
    client = _client("hafta8_recovery.json")
    client.post("/action", data={"action": "acquire", "process": "<script>", "resource": "R1", "amount": "1"})
    html = client.get("/").get_data(as_text=True)
    assert "Geçersiz process ya da kaynak" in html
    assert "<script>" not in html


def test_web_sifir_birim_reddedilir():
    client = _client("hafta8_recovery.json")
    client.post("/action", data={"action": "acquire", "process": "P1", "resource": "R1", "amount": "0"})
    assert "en az 1" in client.get("/").get_data(as_text=True)


def test_web_guvensiz_istek_uyarisi_gosterilir():
    client = _client("hafta6_guvensiz_durum.json")
    client.post("/step")
    client.post("/step")  # P2, R2'yi alıyor → güvensiz
    assert "Son istek sistemi güvensiz duruma soktu" in client.get("/").get_data(as_text=True)


def test_siradaki_olay_aciklamalari():
    from src.dashboard_view import describe_event
    assert describe_event({"action": "terminate", "process": "P2"}) == "Sonlandır: P2"
    assert describe_event({"action": "preempt", "process": "P2", "resource": "R2"}) == "Geri al: R2, sahibi P2"


def test_statik_gorunumde_dongu_var_deadlock_yok_turuncu_serit():
    result = run_scenario.run_scenario_step_by_step(os.path.join(ROOT, "scenarios/hafta4_dongu_deadlock_yok.json"))
    assert 'class="banner warning"' in "".join(result["steps_html"])
