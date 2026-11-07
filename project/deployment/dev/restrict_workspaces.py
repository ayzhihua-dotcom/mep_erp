import sys
def main():
    import frappe, json, os
    frappe.set_user("Administrator")
    hide = ["Selling", "Accounting", "Financial Reports", "Invoicing", "Payments",
            "Assets", "Manufacturing", "CRM", "Support", "Website",
            "Automation", "Build", "Email", "Integrations", "Printing"]
    for n in hide:
        if frappe.db.exists("Workspace", n):
            frappe.db.set_value("Workspace", n, "is_hidden", 1, update_modified=False)
            print("HIDDEN:", n)
        else:
            print("SKIP_NOTFOUND:", n)
    ws_name = "CB 机电总控"
    if not frappe.db.exists("Workspace", ws_name):
        path = "/home/frappe/frappe-bench/apps/cb_erp/cb_erp/fixtures/workspace.json"
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            d = frappe.get_doc(data[0])
            d.standard = 0
            d.is_hidden = 0
            d.public = 1
            d.for_user = None
            d.flags.ignore_links = True
            d.insert(ignore_permissions=True, set_name=ws_name)
            frappe.db.commit()
            print("WS_CREATED:", d.name)
        else:
            print("WS_FIXTURE_NOTFOUND:", path)
    else:
        print("WS_EXISTS:", ws_name)
    frappe.db.commit()
    frappe.clear_cache()
    print("=== VISIBLE WORKSPACES (public & not hidden) ===")
    vis = frappe.get_all("Workspace", fields=["name", "is_hidden", "public"],
                         filters={"is_hidden": 0, "public": 1}, order_by="name asc")
    for v in vis:
        print("  VISIBLE:", v.name)
    print("VISIBLE_COUNT:", len(vis))
    sys.exit(0)
main()
