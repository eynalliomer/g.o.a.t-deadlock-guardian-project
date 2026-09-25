import pytest

from src.bankers import compute_need, is_safe, check_request


def _vec(a, b, c):
    return {"A": a, "B": b, "C": c}


def _kitap_ornegi():
    """Silberschatz 8.6.3.3: 5 process, A=10, B=5, C=7 birim."""
    available = _vec(3, 3, 2)
    maximum = {
        "P0": _vec(7, 5, 3),
        "P1": _vec(3, 2, 2),
        "P2": _vec(9, 0, 2),
        "P3": _vec(2, 2, 2),
        "P4": _vec(4, 3, 3),
    }
    allocation = {
        "P0": _vec(0, 1, 0),
        "P1": _vec(2, 0, 0),
        "P2": _vec(3, 0, 2),
        "P3": _vec(2, 1, 1),
        "P4": _vec(0, 0, 2),
    }
    return available, maximum, allocation


def _p1_istegi_verildikten_sonra():
    """Kitapta P4 ve P0 istekleri, P1'in (1,0,2) isteği verildikten sonraki duruma göre değerlendirilir."""
    _, maximum, allocation = _kitap_ornegi()
    allocation["P1"] = _vec(3, 0, 2)
    return _vec(2, 3, 0), maximum, allocation


def test_need_max_eksi_allocation():
    _, maximum, allocation = _kitap_ornegi()
    need = compute_need(maximum, allocation)
    assert need["P0"] == _vec(7, 4, 3)
    assert need["P1"] == _vec(1, 2, 2)
    assert need["P2"] == _vec(6, 0, 0)
    assert need["P3"] == _vec(0, 1, 1)
    assert need["P4"] == _vec(4, 3, 1)


def test_kitap_ornegi_guvenli_ve_sira_kitaptakiyle_ayni():
    safe, sequence = is_safe(*_kitap_ornegi())
    assert safe is True
    assert sequence == ["P1", "P3", "P4", "P0", "P2"]


def test_guvensiz_durum_tespit_edilir():
    available, maximum, allocation = _kitap_ornegi()
    available = _vec(0, 0, 0)  # hiç boş kaynak yok → kimse ihtiyacını karşılayamaz
    safe, sequence = is_safe(available, maximum, allocation)
    assert safe is False
    assert sequence == []


def test_p1_istegi_guvenli_verilebilir():
    decision = check_request("P1", _vec(1, 0, 2), *_kitap_ornegi())
    assert decision.status == "SAFE"
    assert decision.sequence == ["P1", "P3", "P4", "P0", "P2"]


def test_p4_istegi_bosta_yeterli_kaynak_olmadigi_icin_bekler():
    decision = check_request("P4", _vec(3, 3, 0), *_p1_istegi_verildikten_sonra())
    assert decision.status == "WAIT"


def test_p0_istegi_sistemi_guvensiz_duruma_sokar():
    decision = check_request("P0", _vec(0, 2, 0), *_p1_istegi_verildikten_sonra())
    assert decision.status == "UNSAFE"


def test_max_ustu_istek_hata_verir():
    with pytest.raises(ValueError):
        check_request("P3", _vec(0, 2, 0), *_kitap_ornegi())  # P3'ün Need'i (0,1,1)


def test_check_request_girdileri_degistirmez():
    available, maximum, allocation = _kitap_ornegi()
    check_request("P1", _vec(1, 0, 2), available, maximum, allocation)
    assert available == _vec(3, 3, 2)
    assert allocation["P1"] == _vec(2, 0, 0)
