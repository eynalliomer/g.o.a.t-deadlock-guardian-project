import pytest

from src.app import create_app


@pytest.fixture
def client():
    app = create_app("hafta8_recovery.json")
    app.config["TESTING"] = True
    return app.test_client()


def _page(client):
    return client.get("/").get_data(as_text=True)


def test_dashboard_acilir(client):
    html = _page(client)
    assert "Deadlock Guardian" in html
    assert "hafta8_recovery.json" in html
    assert "RİSK: LOW" in html
    assert "<svg" in html  # RAG çizimi


def test_sonraki_olay_dugmesi_simulasyonu_ilerletir(client):
    response = client.post("/step")
    assert response.status_code == 302  # POST → yönlendir → GET
    html = _page(client)
    assert "Olay 1 / 10" in html


def test_deadlockta_kurtarma_secenegi_dugmeyle_uygulanir(client):
    for _ in range(4):
        client.post("/step")
    html = _page(client)
    assert "RİSK: CRITICAL" in html
    assert 'action="/option/0"' in html

    client.post("/option/0")
    html = _page(client)
    assert "RİSK: CRITICAL" not in html
    assert "Geri al: R2, sahibi P2" in html


def test_geri_al_ve_sifirla(client):
    client.post("/step")
    client.post("/step")
    client.post("/undo")
    assert "Olay 1 / 10" in _page(client)
    client.post("/reset")
    assert "Olay 0 / 10" in _page(client)


def test_elle_eylem_formu(client):
    client.post("/action", data={"action": "acquire", "process": "P2", "resource": "R1", "amount": "1"})
    html = _page(client)
    assert "P2, R1&#39;den 1 birim istiyor" in html or "P2, R1'den 1 birim istiyor" in html


def test_hatali_eylem_sayfayi_cokertmez_hata_mesaji_gosterir(client):
    client.post("/action", data={"action": "release", "process": "P1", "resource": "R1", "amount": "1"})
    html = _page(client)
    assert "class=\"error\"" in html
    assert "Olay 0 / 10" in html


def test_senaryo_degistirilebilir(client):
    client.post("/load", data={"scenario": "hafta4_deadlock.json"})
    assert "hafta4_deadlock.json" in _page(client)


def test_senaryo_klasoru_disindaki_dosya_yuklenemez(client):
    client.post("/load", data={"scenario": "../README.md"})
    html = _page(client)
    assert "class=\"error\"" in html
    assert "hafta8_recovery.json" in html  # eski senaryo yerinde kaldı
