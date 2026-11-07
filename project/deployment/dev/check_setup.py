import sys
def main():
    import frappe
    def safe(fn, label):
        try:
            print(label, "->", fn())
        except Exception as e:
            print(label, "ERR:", repr(e))
    try:
        safe(lambda: frappe.db.get_value("Website Settings", "Website Settings", "setup_complete"), "SETUP_WEBSITE")
        safe(lambda: bool(frappe.db.count("Company")), "HAS_COMPANY")
        safe(lambda: frappe.db.sql("select name from tabCompany", as_dict=False), "COMPANIES")
        safe(lambda: frappe.db.get_value("Role", "System Manager", "name"), "SYSMGR_ROLE")
        print("DESK_OK:1")
    except Exception as e:
        print("FATAL:", repr(e))
    sys.exit(0)
main()
