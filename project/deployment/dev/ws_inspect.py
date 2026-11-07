import sys
def main():
    import frappe
    frappe.set_user("Administrator")
    rows = frappe.get_all("Workspace", fields=["name", "label", "module", "public", "is_hidden", "restrict_to_domain"], order_by="name asc")
    print("WORKSPACE_COUNT:", len(rows))
    for r in rows:
        print("%s || label=%s || module=%s || public=%s || hidden=%s || domain=%s" % (r.name, r.label, r.module, r.public, r.is_hidden, r.restrict_to_domain))
    print("MODULE_DEFS:")
    mods = frappe.get_all("Module Def", fields=["name", "app_name"], order_by="name asc")
    for m in mods:
        print("  %s || app=%s" % (m.name, m.app_name))
    sys.exit(0)
main()
