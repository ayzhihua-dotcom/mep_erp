import sys
def main():
    import frappe
    frappe.set_user("Administrator")
    if frappe.db.exists("Item Group", "水处理设备类") and not frappe.db.exists("Item Group", "水处理装置"):
        frappe.rename_doc("Item Group", "水处理设备类", "水处理装置", force=True)
        print("RENAMED: 水处理设备类 -> 水处理装置")
    cnt = frappe.db.count("Item", {"item_group": "水处理设备"})
    print("ITEMS_IN_水处理设备:", cnt)
    if cnt and frappe.db.exists("Item Group", "水处理装置"):
        frappe.db.sql("update `tabItem` set item_group=%s where item_group=%s", ("水处理装置", "水处理设备"))
        frappe.db.commit()
        print("MOVED:", cnt, "-> 水处理装置")
    bad = frappe.db.sql("select i.item_group g, count(*) c from `tabItem` i join `tabItem Group` ig on ig.name=i.item_group where ig.is_group=1 group by i.item_group", as_dict=True)
    print("REMAINING_GROUP_NODES_WITH_ITEMS:", bad)
    print("GROUPS_END_类:", frappe.get_all("Item Group", filters={"item_group_name": ["like", "%类"]}, pluck="name"))
    print("TOTAL_ITEMS:", frappe.db.count("Item"))
    print("TOTAL_GROUPS:", frappe.db.count("Item Group"))
    sys.exit(0)
main()
