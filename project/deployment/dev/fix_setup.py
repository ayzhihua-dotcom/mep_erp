import sys
def main():
    import frappe
    try:
        print("table_exists:", frappe.db.table_exists("Installed Application"))
        rows = frappe.get_all("Installed Application", fields=["name","app_name","is_setup_complete"])
        print("ROWS:", rows)
        for row in rows:
            if row["app_name"] in ("frappe","erpnext"):
                d = frappe.get_doc("Installed Application", row["name"])
                old = getattr(d,"is_setup_complete",None)
                d.is_setup_complete = 1
                d.save(ignore_permissions=True)
                print("SET", row["app_name"], "was", old, "-> now", frappe.db.get_value("Installed Application", row["name"],"is_setup_complete"))
        frappe.db.commit()
        print("RESULT is_setup_complete():", frappe.is_setup_complete())
    except Exception as e:
        print("ERR:", repr(e))
        frappe.db.rollback()
    sys.exit(0)
main()
