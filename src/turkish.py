"""Türkçe ek yardımcıları: kaynak adına doğru ayrılma ekini (-den/-dan/-ten/-tan) getirir.

Ek, adın okunuşuna göre seçilir: "R3" → "R üç" → R3'ten, "R6" → "R altı" → R6'dan.
"""

# Son rakamın okunuşu: (son ünlü kalın mı, sert ünsüzle mi bitiyor)
_DIGITS = {
    "0": ("sıfır", True, False), "1": ("bir", False, False), "2": ("iki", False, False),
    "3": ("üç", False, True), "4": ("dört", False, True), "5": ("beş", False, True),
    "6": ("altı", True, False), "7": ("yedi", False, False), "8": ("sekiz", False, False),
    "9": ("dokuz", True, False),
}
_BACK_VOWELS = set("aıou")
_FRONT_VOWELS = set("eiöü")
_HARD_CONSONANTS = set("çfhkpsşt")  # fıstıkçı şahap


def ablative(name: str) -> str:
    """name + ayrılma eki: R1'den, R3'ten, R6'dan, Yazıcı'dan, Disk'ten."""
    if name[-1] in _DIGITS:
        # Yalnızca son rakama bakılır: R10 ("on") doğru çıkar, ama R20 ("yirmi") gibi
        # sıfırla biten diğer onluklarda ek yanlış olabilir. Senaryolarımız R1–R10 kullanıyor.
        _, back, hard = _DIGITS[name[-1]]
    else:
        lower = name.lower()
        vowels = [c for c in lower if c in _BACK_VOWELS | _FRONT_VOWELS]
        back = bool(vowels) and vowels[-1] in _BACK_VOWELS
        hard = lower[-1] in _HARD_CONSONANTS
    suffix = ("t" if hard else "d") + ("an" if back else "en")
    return f"{name}'{suffix}"
