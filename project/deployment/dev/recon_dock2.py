import sys
def main():
    import frappe
    frappe.set_user("Administrator")
    for dt in ["Dock", "Dock Item"]:
        m = frappe.get_meta(dt)
        print("=== ", dt)
        for f in m.fields:
            print("  ", f.fieldname, "|", f.fieldtype, "|", (f.options if f.options else ""))
    # erpnext dock items summary
    d = frappe.get_doc("Dock", "erpnext")
    print("ERPNEXT_DOCK_ITEMS:", [(i.idx, i.link_type, i.link_to, i.title, i.icon, i.hidden) for i in d.items])
    print("HAS_CB_DOCK:", frappe.db.exists("Dock", "cb_erp"))
    sys.exit(0)
main()
