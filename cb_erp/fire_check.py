# -*- coding: utf-8 -*-
def run():
    import frappe
    frappe.set_user("Administrator")
    print("UNDER_FIRE:", frappe.get_all("Item Group", filters={"parent_item_group": "消防"},
                                        fields=["name", "is_group"], order_by="name"))
    for l2 in frappe.get_all("Item Group", filters={"parent_item_group": "消防"}, pluck="name"):
        print("  ", l2, "children:", frappe.db.count("Item Group", {"parent_item_group": l2}))
    return "OK"
