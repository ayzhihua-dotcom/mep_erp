import sys
def main():
    import frappe
    frappe.set_user("Administrator")
    print("ADMIN Project report:", frappe.has_permission("Project", "report"))
    print("ADMIN Report read:", frappe.has_permission("Report", "read"))
    frappe.set_user("chenzhihua@cb.local")
    print("CHEN Project report:", frappe.has_permission("Project", "report"))
    print("CHEN Project read:", frappe.has_permission("Project", "read"))
    print("CHEN Report read:", frappe.has_permission("Report", "read"))
    print("CHEN roles:", [r.role for r in frappe.get_doc("User", "chenzhihua@cb.local").roles])
    print("DOCPERM Project:", frappe.get_all("DocPerm", filters={"parent": "Project"}, fields=["role", "read", "report", "write"]))
    try:
        print("CUSTOM_DOCPERM Project:", frappe.get_all("Custom DocPerm", filters={"parent": "Project"}, fields=["role", "read", "report", "write"]))
    except Exception as e:
        print("CDP_ERR", repr(e))
    sys.exit(0)
main()
