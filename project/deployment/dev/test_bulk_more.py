import sys
def main():
    import frappe
    from frappe.utils import today
    frappe.set_user("Administrator")
    from cb_erp.cb_erp.bulk_ops import api_bulk_submit, api_bulk_cancel, api_bulk_delete, api_bulk_set_project, api_template
    # client script check
    cs = frappe.get_doc("Client Script", "Bulk Entry-Form")
    print("CS_HAS_ADD:", "添加物料行" in (cs.script or ""), "| CS_HAS_TPL:", "下载模板" in (cs.script or ""))
    print("TEMPLATE:", repr(api_template("material_request")[:60]))
    created = []
    try:
        for i in range(2):
            mr = frappe.get_doc({"doctype": "Material Request", "material_request_type": "Purchase",
                                 "company": "中巴机电（巴西）项目有限公司", "custom_cb_project": "PROJ-0001",
                                 "schedule_date": today(),
                                 "items": [{"item_code": "SIM-PV-0001", "qty": 1, "schedule_date": today()}]})
            mr.insert(ignore_permissions=True); created.append(mr.name)
        frappe.db.commit()
        print("DRAFTS:", created)
        print("SET_PROJECT:", api_bulk_set_project("Material Request", created, "PROJ-0002"))
        print("PROJ_AFTER:", [frappe.db.get_value("Material Request", n, "custom_cb_project") for n in created])
        print("SUBMIT:", api_bulk_submit("Material Request", created))
        print("DS_AFTER_SUBMIT:", [frappe.db.get_value("Material Request", n, "docstatus") for n in created])
        print("CANCEL:", api_bulk_cancel("Material Request", created))
        print("DS_AFTER_CANCEL:", [frappe.db.get_value("Material Request", n, "docstatus") for n in created])
        print("DELETE:", api_bulk_delete("Material Request", created))
        print("EXISTS_AFTER_DELETE:", [frappe.db.exists("Material Request", n) for n in created])
    except Exception as e:
        print("ERR:", repr(e))
        import traceback; traceback.print_exc()
    finally:
        for n in created:
            try:
                if frappe.db.exists("Material Request", n):
                    d = frappe.get_doc("Material Request", n)
                    if d.docstatus == 1: d.cancel()
                    frappe.delete_doc("Material Request", n, force=True)
            except Exception: pass
        frappe.db.commit()
        print("FINAL_MR_COUNT:", frappe.db.count("Material Request"))
    sys.exit(0)
main()
