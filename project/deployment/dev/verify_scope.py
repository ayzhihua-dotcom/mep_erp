import sys
def main():
    import frappe
    frappe.set_user("Administrator")
    import cb_erp.cb_erp.workspace_setup as ws
    ws.after_migrate()
    print("AFTER_MIGRATE_CALLED_OK")
    vis = frappe.get_all("Workspace", fields=["name"], filters={"is_hidden": 0, "public": 1}, order_by="name asc")
    for v in vis:
        print("VISIBLE:", v.name)
    print("VISIBLE_COUNT:", len(vis))
    ws_doc = frappe.get_doc("Workspace", "CB 机电总控")
    print("CB_LINKS:", len(ws_doc.links))
    print("CB_SHORTCUTS:", len(ws_doc.shortcuts))
    sys.exit(0)
main()
