import sys
def main():
    import frappe
    frappe.set_user("Administrator")
    FNS = ["custom_seq", "custom_uom", "custom_use_project", "custom_responsible", "custom_spec", "custom_remark"]
    for dt in ["Material Request Item", "Stock Entry Detail", "Purchase Order Item", "Stock Reconciliation Item"]:
        have = [fn for fn in FNS if frappe.db.has_column(dt, fn)]
        m = frappe.get_meta(dt)
        ilv = {fn: (m.get_field(fn).in_list_view if m.get_field(fn) else None) for fn in have}
        print("COLS", dt, "| have:", have, "| in_list_view:", ilv)
    from cb_erp.cb_erp.bulk_ops import api_create
    rows = [{"item_code": "SIM-PV-0005", "item_name": "x", "spec": "DN150 PN16", "unit": "米", "qty": 3, "remark": "测试备注"}]
    res = api_create("material_issue", rows, project="PROJ-0005", warehouse="巴西现场总仓 - 巴项",
                     discipline="管道", system="工艺系统", responsible="eng02@cb.local")
    print("RES", res)
    if res.get("created"):
        n = res["created"][0]["name"]
        print("LINES", frappe.get_all("Stock Entry Detail", filters={"parent": n},
              fields=["item_code", "item_name", "custom_spec", "custom_uom", "qty",
                      "custom_use_project", "custom_responsible", "custom_remark", "custom_seq"]))
    sys.exit(0)
main()
