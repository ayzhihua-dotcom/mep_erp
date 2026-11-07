# -*- coding: utf-8 -*-
def run():
    import frappe
    frappe.set_user("Administrator")
    fire_groups = []
    for l2 in ("消防水", "消防电"):
        fire_groups += frappe.get_all("Item Group", filters={"parent_item_group": l2}, pluck="name")
    codes = frappe.get_all("Item", filters={"item_group": ["in", fire_groups]}, pluck="name")
    print("FIRE_ITEMS:", len(codes))
    tables = [
        ("Stock Ledger Entry", "item_code"),
        ("Stock Entry Detail", "item_code"),
        ("Purchase Order Item", "item_code"),
        ("Material Request Item", "item_code"),
        ("BOM Item", "item_code"),
        ("Bin", "item"),
        ("Item Price", "item_code"),
        ("Material Commitment", "item_code"),
    ]
    chunk = 500
    for dt, col in tables:
        if not frappe.db.table_exists(dt):
            continue
        total = 0
        for i in range(0, len(codes), chunk):
            part = codes[i:i + chunk]
            total += frappe.db.count(dt, {col: ["in", part]})
        print("REF", dt, total)
    # 有多少是泛化名称（xxx-0001）
    generic = frappe.db.sql("""select count(*) c from `tabItem`
                               where item_group in %(g)s and item_name regexp '^[^-]+-[0-9]{4}$'""",
                            {"g": fire_groups}, as_dict=True)
    print("GENERIC_NAMES:", generic[0]["c"])
    return "OK"
