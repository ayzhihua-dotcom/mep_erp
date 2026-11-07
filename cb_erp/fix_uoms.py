# -*- coding: utf-8 -*-
def run():
    import frappe
    frappe.set_user("Administrator")
    for u in ("台", "具"):
        if not frappe.db.exists("UOM", u):
            frappe.get_doc({"doctype": "UOM", "uom_name": u, "enabled": 1,
                            "must_be_whole_number": 1}).insert(ignore_permissions=True)
            print("CREATED_UOM", u)
    frappe.db.commit()
    frappe.clear_cache()
    bad = frappe.db.sql("""select i.stock_uom u, count(*) c from `tabItem` i
                           left join `tabUOM` uo on uo.name=i.stock_uom
                           where uo.name is null group by i.stock_uom""", as_dict=True)
    print("INVALID_ITEM_UOMS:", [(b["u"], b["c"]) for b in bad])
    return "OK"
