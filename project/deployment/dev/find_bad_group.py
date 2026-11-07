import sys
def main():
    import frappe
    frappe.set_user("Administrator")
    rows = frappe.db.sql("""
        select i.item_group as g, ig.is_group, ig.parent_item_group as parent, count(*) c
        from `tabItem` i join `tabItem Group` ig on ig.name = i.item_group
        where ig.is_group = 1 group by i.item_group, ig.is_group, ig.parent_item_group
    """, as_dict=True)
    print("GROUP_NODES_WITH_ITEMS:", rows)
    sys.exit(0)
main()
