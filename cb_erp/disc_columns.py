# -*- coding: utf-8 -*-
def run():
    import frappe
    frappe.set_user("Administrator")
    dts = ("Material Request", "Purchase Order", "Stock Entry", "Purchase Receipt")
    frappe.db.sql("""update `tabCustom Field` set in_list_view=1
                     where dt in %s and fieldname in ('custom_discipline','custom_system')""", (dts,))
    frappe.db.commit()
    frappe.clear_cache()
    print("LIST_VIEW_SET:", dts)
    print("MR_TEST_DOCS:", frappe.get_all("Material Request",
                                          filters={"name": ["like", "MAT-MR-2026-0006%"]},
                                          fields=["name", "custom_discipline", "custom_system", "docstatus"]))
    return "OK"
