import sys
def main():
    import frappe
    frappe.set_user("Administrator")
    from cb_erp.cb_erp.alerts import run_all_rules
    from frappe.utils import today
    proj = "PROJ-0001"
    item = "CB-GV-001"
    ev_names = []
    mr_name = None
    try:
        mr = frappe.get_doc({
            "doctype": "Material Request",
            "material_request_type": "Purchase",
            "company": "中巴机电（巴西）项目有限公司",
            "custom_cb_project": proj,
            "schedule_date": today(),
            "items": [{"item_code": item, "qty": 5, "schedule_date": today()}],
        })
        mr.insert(ignore_permissions=True)
        mr_name = mr.name
        mr.submit()
        frappe.db.commit()
        print("TEMP_MR:", mr_name, "| ds:", frappe.db.get_value("Material Request", mr_name, "docstatus"))
        out1 = run_all_rules()
        print("RUN1:", out1)
        evs = frappe.get_all("Alert Event", filters={"rule_code": "ALR-001", "ref_docname": mr_name},
                             fields=["name", "alert_type", "metric_value", "severity", "status", "dedupe_key", "project", "item_code"])
        print("EVENTS_RUN1_COUNT:", len(evs))
        for e in evs:
            print("EV:", e.name, "|", e.alert_type, "| metric:", e.metric_value, "| severity:", e.severity, "| status:", e.status, "| proj:", e.project, "|", e.item_code)
            ev_names.append(e.name)
        out2 = run_all_rules()
        print("RUN2:", out2)
        evs2 = frappe.get_all("Alert Event", filters={"rule_code": "ALR-001", "ref_docname": mr_name}, fields=["name"])
        print("EVENTS_RUN2_COUNT(dedupe->should stay 1):", len(evs2))
        print("ALERT_EVENT_TOTAL:", frappe.db.count("Alert Event"))
    except Exception as e:
        print("ALERT_TEST_ERR:", repr(e))
        import traceback
        traceback.print_exc()
        try:
            frappe.db.rollback()
        except Exception:
            pass
    finally:
        try:
            # cleanup alert events + notifications
            all_ev = frappe.get_all("Alert Event", filters={"ref_docname": mr_name} if mr_name else {"name": ["in", ev_names]}, fields=["name"])
            names = [x.name for x in all_ev] + ev_names
            names = list(set(names))
            for n in names:
                frappe.db.sql("delete from `tabNotification Log` where document_type='Alert Event' and document_name=%s", (n,))
                if frappe.db.exists("Alert Event", n):
                    frappe.delete_doc("Alert Event", n, force=True)
            frappe.db.commit()
            print("ALERT_EVENTS_DELETED:", len(names))
            if mr_name and frappe.db.exists("Material Request", mr_name):
                d = frappe.get_doc("Material Request", mr_name)
                if d.docstatus == 1:
                    d.cancel(); frappe.db.commit(); print("MR_CANCELLED")
                frappe.delete_doc("Material Request", mr_name, force=True); frappe.db.commit(); print("MR_DELETED")
            print("FINAL_ALERT_EVENT_COUNT:", frappe.db.count("Alert Event"))
            print("FINAL_MR_COUNT:", frappe.db.count("Material Request"))
        except Exception as e:
            print("CLEANUP_ERR:", repr(e))
            import traceback
            traceback.print_exc()
    sys.exit(0)
main()
