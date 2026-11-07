import sys
def main():
    import frappe
    frappe.set_user("Administrator")
    from cb_erp.cb_erp.bulk_ops import api_create
    res = api_create("material_request", [{"item_code": "SIM-PV-0001", "qty": 1}],
                     project="PROJ-0001", discipline="电气", system="电气系统", responsible="eng01@cb.local")
    print("RESULT:", res)
    if res.get("created"):
        n = res["created"][0]["name"]
        mr = frappe.get_doc("Material Request", n)
        print("DOC:", n, "| discipline:", mr.get("custom_discipline"), "| system:", mr.get("custom_system"),
              "| responsible:", mr.get("custom_responsible"), "| owner:", mr.owner)
        mr.cancel(); frappe.db.commit()
        mr.delete(force=True); frappe.db.commit()
        print("CLEANED")
    print("MR_COUNT:", frappe.db.count("Material Request"))
    sys.exit(0)
main()
