from src.html_view import render_step, save_html
from src.resource import Resource


def test_sayfa_adim_gezinme_kontrollerini_icerir(tmp_path):
    steps = [render_step(f"{i}. adım", [], [Resource("R1")]) for i in range(3)]
    out = save_html(steps, out_path=str(tmp_path / "view.html"))
    html = open(out, encoding="utf-8").read()

    assert html.count('<section class="step">') == 3  # bütün adımlar sayfada, JS yalnızca gizliyor
    assert 'id="prev"' in html and 'id="next"' in html
    assert 'id="toggle-all"' in html
    assert 'id="counter"' in html
    assert "ArrowRight" in html and "ArrowLeft" in html
