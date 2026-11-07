import sys
def main():
    import frappe
    frappe.set_user("Administrator")
    from frappe.desk.doctype.dock.dock import get_app_entry_set, resolve_dock, get_dock, dock_records, permitted_workspaces
    print("DOCK_RECORDS:", dock_records())
    d = get_dock("frappe", standard=1)
    print("STANDARD_DOCK:", d.name if d else None)
    if d:
        print("ITEMS:", [(i.link_type, i.link_to, i.title, i.icon) for i in d.items])
    print("ENTRY_SET:", [(e.get("link_type"), e.get("link_to"), e.get("title")) for e in get_app_entry_set("frappe")])
    print("PERMITTED_HAS_WS:", "巴西机电ERP系统测试" in permitted_workspaces())
    sys.exit(0)
main()
