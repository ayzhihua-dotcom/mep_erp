import sys
def main():
    import frappe
    frappe.set_user("Administrator")
    rows = frappe.db.sql("select item_group, count(*) c from `tabItem` group by item_group order by c asc", as_dict=True)
    print("LEAF_WITH_ITEMS:", len(rows))
    print("MIN_LEAF:", rows[0] if rows else None)
    print("MAX_LEAF:", rows[-1] if rows else None)
    bad = frappe.db.sql("select count(*) c from `tabItem` i join `tabItem Group` ig on ig.name=i.item_group where ig.is_group=1", as_dict=True)
    print("ITEMS_IN_GROUP_NODES:", bad)
    for s in frappe.get_all("Item", fields=["item_code", "item_name", "item_group", "stock_uom", "valuation_rate", "is_stock_item"], limit=3, order_by="item_code desc"):
        print("SAMPLE:", s)
    print("TOTAL_ITEMS:", frappe.db.count("Item"))
    print("TOTAL_GROUPS:", frappe.db.count("Item Group"))
    sys.exit(0)
main()
