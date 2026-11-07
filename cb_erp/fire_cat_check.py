# -*- coding: utf-8 -*-
def run():
    import frappe
    frappe.set_user("Administrator")
    from cb_erp.cb_erp.bulk_ops import api_list_categories, api_search_items
    print("ROOT_CHILDREN:", frappe.get_all("Item Group", filters={"parent_item_group": "所有物料组"}, pluck="name"))
    print("API_CATS:", api_list_categories())
    print("ROOT_EXISTS:", frappe.db.exists("Item Group", "所有物料组"))
    print("FIRE_CHILD:", frappe.get_all("Item Group", filters={"parent_item_group": "消防"}, fields=["name", "is_group"]))
    print("SEARCH_FIRE:", [(r["item_code"], r["item_name"], r["custom_spec"]) for r in api_search_items(keyword="", category="消防", limit=3)])
    return "OK"
