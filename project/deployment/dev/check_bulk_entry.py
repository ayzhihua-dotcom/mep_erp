import sys
def main():
    import frappe
    frappe.set_user("Administrator")
    frappe.clear_cache()
    print("DOCTYPE_EXISTS:", frappe.db.exists("DocType", "Bulk Entry"))
    print("TABLE_EXISTS:", frappe.db.table_exists("Bulk Entry"))
    print("CLIENT_SCRIPTS:", frappe.get_all("Client Script", filters={"dt": "Bulk Entry"}, fields=["name", "view", "enabled"]))
    ws = frappe.get_doc("Workspace", "CB 机电总控")
    print("WS_HAS_BULK:", any(l.link_to == "Bulk Entry" for l in ws.links))
    if not any(l.link_to == "Bulk Entry" for l in ws.links):
        try:
            ws.append("links", {"type": "Link", "label": "批量录入", "link_to": "Bulk Entry", "link_type": "DocType"})
            ws.save(ignore_permissions=True)
            frappe.db.commit()
            print("WS_LINK_ADDED")
        except Exception as e:
            print("WS_LINK_ERR:", repr(e)[:200])
    sys.exit(0)
main()
