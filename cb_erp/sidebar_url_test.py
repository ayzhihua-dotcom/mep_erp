# -*- coding: utf-8 -*-
"""试验：侧栏 URL 用 ../ 抵消应用前缀。"""


def run():
    import frappe
    frappe.set_user("Administrator")
    sb = frappe.get_doc("Sidebar", "Stock")
    # 移除本应用加的入口
    kept = []
    for i in sb.items:
        if (i.label or "") in ("物料领用（出库）", "物料入库", "物料退料（批量）", "库存盘点（新建）"):
            continue
        kept.append(i)
    sb.set("items", [])
    for i in kept:
        sb.append("items", {k: i.get(k) for k in
                            ("label", "link_type", "link_to", "url", "icon", "route_options",
                             "hidden", "open_in_new_tab", "indent", "collapsible")})

    anchor = None
    for i in sb.items:
        if i.link_type == "DocType" and i.link_to == "Stock Entry":
            anchor = i.idx
    url_items = [
        ("物料领用（出库）", "/desk/stock/stock-entry/new?stock_entry_type=Material%20Issue"),
        ("物料入库", "/desk/stock/stock-entry/new?stock_entry_type=Material%20Receipt"),
        ("物料退料（入库）", "/desk/stock/stock-entry/new?stock_entry_type=Material%20Receipt&is_return=1"),
    ]
    pos = anchor
    for label, url in url_items:
        pos += 1
        row = sb.append("items", {"label": label, "link_type": "URL", "url": url,
                                  "icon": "shelf-rack-soft"})
        row.idx = pos
    sb.save(ignore_permissions=True)
    frappe.db.commit()
    print("SIDEBAR_URL_TEST_DONE")
    return "OK"
