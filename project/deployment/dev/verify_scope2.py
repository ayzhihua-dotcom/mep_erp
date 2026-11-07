import sys
def main():
    import frappe
    frappe.set_user("Administrator")
    import cb_erp.cb_erp.workspace_setup as ws
    ws.after_migrate()
    print("AFTER_MIGRATE_OK")
    vis = frappe.get_all("Workspace", fields=["name"], filters={"is_hidden": 0, "public": 1}, order_by="name asc")
    print("VISIBLE_WORKSPACES:", [v.name for v in vis])
    frappe.set_user("chenzhihua@cb.local")
    from frappe.boot import get_module_sidebars
    from frappe.desk.doctype.sidebar.sidebar import get_navigable_modules
    print("SIDEBARS:", sorted(get_module_sidebars().keys()))
    print("NAVIGABLE:", get_navigable_modules())
    frappe.set_user("Administrator")
    sys.exit(0)
main()
