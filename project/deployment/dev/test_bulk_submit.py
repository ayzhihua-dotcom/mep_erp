import sys
def main():
    import frappe
    from frappe.utils import today
    frappe.set_user("Administrator")
    from cb_erp.cb_erp.bulk_ops import api_bulk_submit
    created = []
    try:
        for i in range(2):
            mr = frappe.get_doc({"doctype": "Material Request", "material_request_type": "Purchase",
                                 "company": "中巴机电（巴西）项目有限公司", "custom_cb_project": "PROJ-0001",
                                 "schedule_date": today(),
                                 "items": [{"item_code": "SIM-PV-0001", "qty": 1, "schedule_date": today()}]})
            mr.insert(ignore_permissions=True)
            created.append(mr.name)
        frappe.db.commit()
        print("DRAFTS:", created)
        print("BEFORE_DS:", [(n, frappe.db.get_value("Material Request", n, "docstatus")) for n in created])
        res = api_bulk_submit("Material Request", created)
        print("RESULT:", res)
        print("AFTER_DS:", [(n, frappe.db.get_value("Material Request", n, "docstatus")) for n in created])
    except Exception as e:
        print("ERR:", repr(e))
        import traceback; traceback.print_exc()
    finally:
        for n in created:
            try:
                if frappe.db.exists("Material Request", n):
                    d = frappe.get_doc("Material Request", n)
                    if d.docstatus == 1:
                        d.cancel(); frappe.db.commit()
                    frappe.delete_doc("Material Request", n, force=True)
            except Exception as e:
                print("CLEANUP_ERR", n, repr(e)[:120])
        frappe.db.commit()
        print("CLEANED; MR_COUNT:", frappe.db.count("Material Request"))
    sys.exit(0)
main()
