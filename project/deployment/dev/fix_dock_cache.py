import sys
def main():
    import frappe
    frappe.set_user("Administrator")
    from frappe.desk.doctype.dock.dock import get_app_entry_set, get_dock, DOCK_LAYERS_CACHE_KEY

    # clear every cache that a dock change touches
    frappe.clear_document_cache("Dock", "frappe")
    frappe.clear_document_cache("Dock", "erpnext")
    frappe.cache.delete_value(DOCK_LAYERS_CACHE_KEY)
    frappe.cache.delete_key("bootinfo")
    if hasattr(frappe.local, "dock_cache"):
        del frappe.local.dock_cache
    frappe.db.commit()

    d = get_dock("frappe", standard=1)
    print("ITEMS_NOW:", len(d.items) if d else None)
    print("ENTRY_SET:", [(e.get("link_type"), e.get("link_to")) for e in get_app_entry_set("frappe")])
    sys.exit(0)
main()
