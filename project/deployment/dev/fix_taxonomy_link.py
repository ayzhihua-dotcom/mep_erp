import sys
def main():
    import frappe
    frappe.set_user("Administrator")
    bad2 = frappe.db.sql("select count(*) c from `tabItem` i join `tabItem Group` ig on ig.name=i.item_group where ig.is_group=1", as_dict=True)
    print("ITEMS_IN_GROUP_NODES:", bad2)
    print("ITEM_GROUP_TOTAL:", frappe.db.count("Item Group"), "| ITEM_TOTAL:", frappe.db.count("Item"))
    ws = frappe.get_doc("Workspace", "CB 机电总控")
    if not any(l.link_to == "Item Group" for l in ws.links):
        ws.append("links", {"type": "Link", "label": "物料分类", "link_to": "Item Group", "link_type": "DocType"})
        ws.save(ignore_permissions=True)
        frappe.db.commit()
        print("WS_LINK_ADDED: 物料分类")
    else:
        print("WS_LINK_EXISTS")
    print("WS_LINKS_NOW:", [l.label for l in frappe.get_doc("Workspace", "CB 机电总控").links])
    sys.exit(0)
main()
