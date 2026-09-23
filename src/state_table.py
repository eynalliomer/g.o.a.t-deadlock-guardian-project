def print_state_table(processes: dict, resources: dict):
    print("\n--- Process Tablosu ---")
    print(f"{'Process':<10}{'Durum':<10}{'Elindeki Kaynaklar'}")
    for process in processes.values():
        held = ", ".join(f"{n}x{a}" for n, a in process.held_resources.items()) or "—"
        print(f"{process.name:<10}{process.state.name:<10}{held}")

    print("\n--- Resource Tablosu ---")
    print(f"{'Resource':<10}{'Boşta':<8}{'Toplam':<8}{'Dağıtım':<25}{'Bekleyen'}")
    for resource in resources.values():
        allocation = ", ".join(f"{p.name}x{a}" for p, a in resource.allocation.items()) or "—"
        waiting = ", ".join(f"{p.name}({a})" for p, a in resource.waiting_queue) or "—"
        print(
            f"{resource.name:<10}{resource.available_instances:<8}"
            f"{resource.total_instances:<8}{allocation:<25}{waiting}"
        )
