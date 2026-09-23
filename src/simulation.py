from src.process import Process
from src.resource import Resource
from src.html_view import render_step, save_html


def main():
    p1 = Process("P1")
    p2 = Process("P2")
    r1 = Resource("R1")
    steps_html = []

    print("--- Başlangıç ---")
    print(p1, p2, r1, sep="\n")
    steps_html.append(render_step("1. Başlangıç", [p1, p2], [r1]))

    print("\n--- P1, R1'i istiyor ---")
    r1.acquire(p1)
    print(p1, r1, sep="\n")
    steps_html.append(render_step("2. P1, R1'i istiyor", [p1, p2], [r1]))

    print("\n--- P2, R1'i istiyor (meşgul, WAITING olmalı) ---")
    r1.acquire(p2)
    print(p2, r1, sep="\n")
    steps_html.append(render_step("3. P2, R1'i istiyor (meşgul → WAITING)", [p1, p2], [r1]))

    print("\n--- P1, R1'i bırakıyor (R1 otomatik P2'ye geçmeli) ---")
    r1.release(p1)
    print(p1, p2, r1, sep="\n")
    steps_html.append(render_step("4. P1, R1'i bırakıyor → R1 otomatik P2'ye geçiyor", [p1, p2], [r1]))

    out_path = save_html(steps_html)
    print(f"\nGörsel önizleme kaydedildi: {out_path}")


if __name__ == "__main__":
    main()
