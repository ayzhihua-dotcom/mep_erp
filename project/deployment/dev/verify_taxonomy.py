import sys
def main():
    import frappe
    frappe.set_user("Administrator")
    root = "所有物料组"
    l1s = frappe.get_all("Item Group", filters={"parent_item_group": root},
                         fields=["item_group_name", "is_group"], order_by="item_group_name")
    print("ROOT_CHILDREN(L1):", len(l1s))
    for l1 in l1s:
        l2s = frappe.get_all("Item Group", filters={"parent_item_group": l1.item_group_name},
                             fields=["item_group_name", "is_group"], order_by="item_group_name")
        print("L1:", l1.item_group_name, "| is_group:", l1.is_group, "| L2_count:", len(l2s))
        for l2 in l2s[:2]:
            l3s = frappe.get_all("Item Group", filters={"parent_item_group": l2.item_group_name},
                                 fields=["item_group_name", "is_group"], order_by="item_group_name")
            cnt = sum(frappe.db.count("Item", {"item_group": x.item_group_name}) for x in l3s)
            print("    L2:", l2.item_group_name, "| L3_count:", len(l3s), "| items:", cnt)
    bad = frappe.db.sql("select ig.item_group_name as g, count(i.name) c from `tabItem Group` ig join `tabItem` i on i.item_group=ig.item_group_name where ig.is_group=1 group by ig.item_group_name", as_dict=True)
    print("GROUP_NODES_WITH_ITEMS:", bad)
    bad2 = frappe.db.sql("select count(*) c from `tabItem` i join `tabItem Group` ig on ig.item_group=i.item_group where ig.is_group=1", as_dict=True)
    print("ITEMS_IN_GROUP_NODES:", bad2)
    print("ITEM_GROUP_TOTAL:", frappe.db.count("Item Group"), "| ITEM_TOTAL:", frappe.db.count("Item"))
    ws = frappe.get_doc("Workspace", "CB 机电总控")
    if not any(l.link_to == "Item Group" for l in ws.links):
        ws.append("links", {"type": "Link", "label": "物料分类", "link_to": "Item Group", "link_type": "DocType"})
        ws.save(ignore_permissions=True)
        frappe.db.commit()
        print("WS_LINK_ADDED: 物料分类 (Item Group)")
    else:
        print("WS_LINK_EXISTS: Item Group")
    sys.exit(0)
main()
