# -*- coding: utf-8 -*-
def run():
    import frappe
    frappe.set_user("Administrator")
    chk = [
        ("自动喷水灭火", 6),
        ("消火栓系统", 5),
        ("气体灭火系统", 5),
        ("火灾探测报警", 5),
        ("消防电缆", 4),
        ("防火卷帘控制", 4),
    ]
    for leaf, lim in chk:
        rows = frappe.get_all("Item", filters={"item_group": leaf},
                              fields=["item_code", "item_name", "custom_spec", "stock_uom"],
                              limit=lim, order_by="item_code")
        print("==", leaf)
        for r in rows:
            print("   ", r["item_code"], "|", r["item_name"], "|", r["custom_spec"], "|", r["stock_uom"])
    total = 0
    for l2 in ("消防水", "消防电"):
        for lf in frappe.get_all("Item Group", filters={"parent_item_group": l2}, pluck="name"):
            total += frappe.db.count("Item", {"item_group": lf})
    print("FIRE_ITEM_TOTAL:", total)
    return "OK"
