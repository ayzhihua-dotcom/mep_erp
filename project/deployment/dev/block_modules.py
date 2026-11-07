import sys
def main():
    import frappe
    frappe.set_user("Administrator")
    BLOCK = ["Accounts", "Selling", "Assets", "Manufacturing", "CRM", "Support",
             "Website", "Automation", "Build", "Email", "Integrations", "Printing"]
    users = frappe.get_all("User", filters={"enabled": 1, "user_type": "System User"}, fields=["name"])
    targets = [u.name for u in users if u.name not in ("Administrator", "Guest")]
    print("TARGET_USERS:", targets)
    for uname in targets:
        u = frappe.get_doc("User", uname)
        existing = {b.module for b in u.block_modules}
        added = [m for m in BLOCK if m not in existing]
        if added:
            for m in added:
                u.append("block_modules", {"module": m})
            u.flags.ignore_permissions = True
            u.save()
            print("BLOCKED_ADDED:", uname, added)
        else:
            print("ALREADY_BLOCKED:", uname)
    frappe.db.commit()
    frappe.clear_cache()
    if frappe.db.exists("User", "chenzhihua@cb.local"):
        frappe.set_user("chenzhihua@cb.local")
        from frappe.desk.doctype.sidebar.sidebar import get_navigable_modules
        from frappe.boot import get_module_sidebars
        print("CHENZHIHUA_NAVIGABLE:", get_navigable_modules())
        print("CHENZHIHUA_SIDEBARS:", sorted(get_module_sidebars().keys()))
        frappe.set_user("Administrator")
    sys.exit(0)
main()
