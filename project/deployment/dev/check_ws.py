import sys
def main():
    import frappe
    frappe.set_user("Administrator")
    print("WS_EXISTS:", frappe.db.exists("Workspace", "CB 机电总控"))
    if frappe.db.exists("Workspace", "CB 机电总控"):
        ws = frappe.get_doc("Workspace", "CB 机电总控")
        print("hidden:", ws.is_hidden, "| public:", ws.public, "| links:", len(ws.links))
        print("labels:", [l.label for l in ws.links])
    print("CB_PAGES:", frappe.get_all("Page", filters={"module": "CB ERP"}, pluck="name"))
    try:
        hooks = frappe.get_hooks("add_to_apps_screen")
        print("ADD_TO_APPS:", hooks)
    except Exception as e:
        print("HOOK_ERR", repr(e))
    # visible workspaces
    print("VISIBLE:", frappe.get_all("Workspace", filters={"is_hidden": 0, "public": 1}, pluck="name", order_by="name"))
    sys.exit(0)
main()
