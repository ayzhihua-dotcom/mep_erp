import sys
def main():
    import frappe
    frappe.set_user("Administrator")
    for dt in ["Material Request", "Stock Entry", "Purchase Order", "Stock Reconciliation",
               "Material Budget", "Material Commitment", "CB Import Case", "CB Shipment"]:
        try:
            m = frappe.get_meta(dt)
            print(dt, "| remarks:", bool(m.get_field("remarks")), "| owner_col:", frappe.db.has_column(dt, "owner"))
        except Exception as e:
            print(dt, "ERR", repr(e)[:80])
    try:
        cf = frappe.get_doc({"doctype": "Custom Field", "dt": "Material Request",
                             "fieldname": "custom_test_disc", "fieldtype": "Data",
                             "label": "测试专业", "insert_after": "custom_cb_project"})
        cf.insert(ignore_permissions=True)
        frappe.db.commit()
        print("CF_OK")
        frappe.delete_doc("Custom Field", cf.name, force=True)
        frappe.db.commit()
    except Exception as e:
        print("CF_ERR:", repr(e)[:200])
    print("L1:", [g.item_group_name for g in frappe.get_all("Item Group", filters={"parent_item_group": "所有物料组"}, fields=["item_group_name"])])
    sys.exit(0)
main()
