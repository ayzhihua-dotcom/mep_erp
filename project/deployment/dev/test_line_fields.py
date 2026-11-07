import sys
def main():
    import frappe
    frappe.set_user("Administrator")
    from cb_erp.cb_erp.bulk_ops import api_create
    rows = [{"item_code": "SIM-PV-0004", "item_name": "钢管-DN100", "spec": "φ114×4.0", "qty": 2, "remark": "演示：规格备注"}]
    res = api_create("material_issue", rows, project="PROJ-0004", warehouse="巴西现场总仓 - 巴项",
                     discipline="管道", system="工艺系统", responsible="eng01@cb.local")
    print("RES:", res)
    if res.get("created"):
        n = res["created"][0]["name"]
        sed = frappe.get_all("Stock Entry Detail", filters={"parent": n},
                             fields=["item_code", "item_name", "custom_spec", "custom_remark", "qty"])
        print("LINES:", sed)
    sys.exit(0)
main()
