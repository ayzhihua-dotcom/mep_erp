import sys
def main():
    import frappe
    frappe.set_user("Administrator")
    ws = frappe.get_doc("Workspace", "巴西机电ERP系统测试")
    print("BEFORE label:", ws.label, "| title:", ws.title)
    ws.label = "巴西机电ERP系统测试"
    ws.title = "巴西机电ERP系统测试"
    ws.save(ignore_permissions=True)
    frappe.db.commit()
    frappe.clear_cache()
    print("AFTER label:", ws.label, "| title:", ws.title)
    sys.exit(0)
main()
