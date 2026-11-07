import sys
def main():
    import frappe
    frappe.set_user("Administrator")
    from cb_erp.cb_erp.alerts import run_all_rules
    from frappe.utils import today, add_days
    created = []
    try:
        t_over = frappe.get_doc({
            "doctype": "Task", "subject": "临时-逾期任务", "project": "PROJ-0001",
            "status": "Open", "priority": "High", "is_milestone": 0,
            "exp_start_date": add_days(today(), -4) + " 09:00:00",
            "exp_end_date": add_days(today(), -3) + " 18:00:00",
        })
        t_over.insert(ignore_permissions=True); created.append(("Task", t_over.name))
        t_ms = frappe.get_doc({
            "doctype": "Task", "subject": "临时-临期里程碑", "project": "PROJ-0001",
            "status": "Open", "priority": "High", "is_milestone": 1,
            "exp_start_date": add_days(today(), 1) + " 09:00:00",
            "exp_end_date": add_days(today(), 3) + " 18:00:00",
        })
        t_ms.insert(ignore_permissions=True); created.append(("Task", t_ms.name))
        frappe.db.commit()
        print("TEMP_TASKS:", [n for _, n in created])
        out = run_all_rules()
        print("RUN:", out)
        evs = frappe.get_all("Alert Event", fields=["name", "rule_code", "alert_type", "metric_value", "ref_docname", "status"])
        print("EVENT_COUNT:", len(evs))
        for e in evs:
            print("EV:", e.name, "|", e.rule_code, "|", e.alert_type, "| metric:", e.metric_value, "| ref:", e.ref_docname, "| status:", e.status)
        # dedupe
        out2 = run_all_rules()
        print("RUN2:", out2)
        print("EVENT_COUNT_AFTER_RUN2:", frappe.db.count("Alert Event"))
    except Exception as e:
        print("TEST_ERR:", repr(e))
        import traceback; traceback.print_exc()
        try: frappe.db.rollback()
        except Exception: pass
    finally:
        try:
            evs = frappe.get_all("Alert Event", pluck="name")
            for n in evs:
                frappe.db.sql("delete from `tabNotification Log` where document_type='Alert Event' and document_name=%s", (n,))
                frappe.delete_doc("Alert Event", n, force=True)
            frappe.db.commit()
            print("EVENTS_DELETED:", len(evs))
            for dt, name in reversed(created):
                if frappe.db.exists(dt, name):
                    frappe.delete_doc(dt, name, force=True)
            frappe.db.commit()
            print("TEMP_TASKS_DELETED")
            print("FINAL_ALERT_EVENT:", frappe.db.count("Alert Event"))
            print("FINAL_TASK_COUNT:", frappe.db.count("Task"))
        except Exception as e:
            print("CLEANUP_ERR:", repr(e))
            import traceback; traceback.print_exc()
    sys.exit(0)
main()
