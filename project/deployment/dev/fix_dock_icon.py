import sys
def main():
    import frappe
    frappe.set_user("Administrator")
    nm = frappe.db.get_value("Dock Item", {"parent": "erpnext", "link_to": "巴西机电ERP系统测试"}, "name")
    print("DOCK_ITEM:", nm)
    if nm:
        print("OLD_ICON:", frappe.db.get_value("Dock Item", nm, "icon"))
        frappe.db.set_value("Dock Item", nm, "icon", "factory-soft", update_modified=False)
        frappe.db.commit()
        frappe.clear_cache()
        print("ICON_SET: factory-soft")
    sys.exit(0)
main()
