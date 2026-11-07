# -*- coding: utf-8 -*-
def run():
    import frappe
    frappe.set_user("Administrator")
    sb = frappe.get_doc("Sidebar", "Stock")
    existing = {(i.label or "") for i in sb.items}
    anchor = None
    for i in sb.items:
        if i.link_type == "DocType" and i.link_to == "Stock Entry":
            anchor = i.idx
    add = [
        ("物料退料（批量）", "/desk/cb-erp/bulk-entry/new?kind=%E9%80%80%E6%96%99"),
        ("库存盘点（新建）", "/desk/stock/stock-reconciliation/new"),
    ]
    pos = anchor
    n = 0
    for label, url in add:
        if label in existing:
            continue
        pos += 1
        row = sb.append("items", {"label": label, "link_type": "URL", "url": url,
                                  "icon": "shelf-rack-soft"})
        row.idx = pos
        n += 1
    if n:
        sb.save(ignore_permissions=True)
        frappe.db.commit()
    print("ADDED", n)
    return "OK"
