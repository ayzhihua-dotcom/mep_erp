# -*- coding: utf-8 -*-
def run():
    import frappe
    frappe.set_user("Administrator")
    from cb_erp.cb_erp.item_taxonomy_v2 import TAXONOMY
    from cb_erp.cb_erp.bulk_ops import api_search_items, api_list_categories

    l1 = frappe.db.count("Item Group", {"parent_item_group": "所有物料组"})
    l2 = frappe.db.count("Item Group", {"is_group": 1})
    l3 = frappe.db.count("Item Group", {"is_group": 0})
    print("DB_GROUPS L1=%s L2=%s L3=%s TOTAL=%s" % (l1, l2, l3, frappe.db.count("Item Group")))
    print("FILE_TAXONOMY L1=%s L2=%s L3=%s" % (
        len(TAXONOMY),
        sum(len(v) for v in TAXONOMY.values()),
        sum(len(x) for v in TAXONOMY.values() for x in v.values())))
    print("OLD_GROUPS_LEFT:", [g for g in ["消防设备", "消防管件", "消防水系统", "消防报警", "灭火系统",
                                            "喷淋头", "报警阀", "灭火器", "消防管", "消防管配件",
                                            "消火栓", "水流指示器", "消防水箱", "消防水池配件",
                                            "火灾探测器", "报警控制器", "声光报警器", "手动报警按钮",
                                            "气体灭火", "泡沫灭火", "消防炮"] if frappe.db.exists("Item Group", g)])
    print("CATS:", api_list_categories())
    for kw, cat in [("喷头", "消防"), ("探测器", "消防"), ("消火栓", None), ("报警", "消防")]:
        rows = api_search_items(keyword=kw, category=cat, limit=5)
        print("SEARCH", kw, cat, "->", [(r["item_code"], r["item_name"], r["custom_spec"], r["stock_uom"], r["category"]) for r in rows])
    # 叶子类是否都挂了物料
    empty = []
    for l2name in ("消防水", "消防电"):
        for lf in frappe.get_all("Item Group", filters={"parent_item_group": l2name}, pluck="name"):
            if not frappe.db.count("Item", {"item_group": lf}):
                empty.append(lf)
    print("EMPTY_LEAVES:", empty)
    sample = frappe.get_all("Item", filters={"item_group": "自动喷水灭火"}, fields=["item_code", "item_name", "custom_spec", "stock_uom"], limit=8)
    for s in sample:
        print("SAMPLE", s["item_code"], s["item_name"], s["custom_spec"], s["stock_uom"])
    return "VERIFY_DONE"
