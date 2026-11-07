# -*- coding: utf-8 -*-
def run():
    import frappe
    frappe.set_user("Administrator")
    name = "MAT-MR-2026-00065"
    if frappe.db.exists("Material Request", name):
        doc = frappe.get_doc("Material Request", name)
        if doc.docstatus == 1:
            doc.cancel()
        frappe.delete_doc("Material Request", name, force=1, ignore_permissions=True)
        frappe.db.commit()
        print("DELETED", name)
    else:
        print("NOT_FOUND")
    return "OK"
