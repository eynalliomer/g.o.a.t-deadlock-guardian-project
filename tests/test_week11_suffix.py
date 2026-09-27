import pytest

from src.turkish import ablative


@pytest.mark.parametrize("name, expected", [
    ("R1", "R1'den"), ("R2", "R2'den"), ("R3", "R3'ten"), ("R4", "R4'ten"), ("R5", "R5'ten"),
    ("R6", "R6'dan"), ("R7", "R7'den"), ("R8", "R8'den"), ("R9", "R9'dan"), ("R10", "R10'dan"),
    ("Yazıcı", "Yazıcı'dan"), ("Disk", "Disk'ten"), ("Modem", "Modem'den"),
])
def test_ayrilma_eki_okunusa_gore_secilir(name, expected):
    assert ablative(name) == expected
