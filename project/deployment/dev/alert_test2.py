import sys
def main():
    import frappe
    frappe.set_user("Administrator")
    from cb_erp.cb_erp.alerts import run_all_rules
    from frappe.utils import today, add_days
    created = []
    try:
        po = frappe.get_all("Purchase Order", pluck="name", limit=1)
        po_name = po[0] if po else None
        print("USE_PO:", po_name)
        # ---- ALR-002: temp import case + overdue undone checklist ----
        ic = frappe.get_doc({
            "doctype": "CB Import Case",
            "company": "中巴机电（巴西）项目有限公司",
            "purchase_order": po_name,
            "customs_status": "单证准备",
            "checklists": [{"doc_name": "提单", "done": 0, "due_date": add_days(today(), -5)}],
        })
        ic.insert(ignore_permissions=True)
        created.append(("CB Import Case", ic.name))
        ic.submit()
        frappe.db.commit()
        print("TEMP_IMPORT_CASE:", ic.name, "| ds:", frappe.db.get_value("CB Import Case", ic.name, "docstatus"))
        # ---- CST-007: temp budget qty=1 + temp commitment qty=3 (same proj/item) ----
        mb = frappe.get_doc({
            "doctype": "Material Budget",
            "company": "中巴机电（巴西）项目有限公司",
            "project": "PROJ-0001",
            "budget_items": [{"item_code": "CB-GV-001", "qty": 1}],
        })
        mb.insert(ignore_permissions=True)
        created.append(("Material Budget", mb.name))
        mb.submit()
        frappe.db.commit()
        print("TEMP_BUDGET:", mb.name, "| ds:", frappe.db.get_value("Material Budget", mb.name, "docstatus"))
        mc = frappe.get_doc({
            "doctype": "Material Commitment",
            "company": "中巴机电（巴西）项目有限公司",
            "project": "PROJ-0001",
            "item_code": "CB-GV-001",
            "qty_committed": 3,
        })
        mc.insert(ignore_permissions=True)
        created.append(("Material Commitment", mc.name))
        mc.submit()
        frappe.db.commit()
        print("TEMP_COMMIT:", mc.name, "| ds:", frappe.db.get_value("Material Commitment", mc.name, "docstatus"))
        # ---- run engine ----
        out = run_all_rules()
        print("RUN:", out)
        evs = frappe.get_all("Alert Event", fields=["name", "rule_code", "alert_type", "metric_value", "ref_docname", "status"])
        print("EVENT_COUNT:", len(evs))
        for e in evs:
            print("EV:", e.name, "|", e.rule_code, "|", e.alert_type, "| metric:", e.metric_value, "| ref:", e.ref_docname, "| status:", e.status)
    except Exception as e:
        print("TEST2_ERR:", repr(e))
        import traceback
        traceback.print_exc()
        try:
            frappe.db.rollback()
        except Exception:
            pass
    finally:
        try:
            # delete all alert events + notifications
            evs = frappe.get_all("Alert Event", pluck="name")
            for n in evs:
                frappe.db.sql("delete from `tabNotification Log` where document_type='Alert Event' and document_name=%s", (n,))
                frappe.delete_doc("Alert Event", n, force=True)
            frappe.db.commit()
            print("ALERT_EVENTS_DELETED:", len(evs))
            for dt, name in reversed(created):
                if frappe.db.exists(dt, name):
                    d = frappe.get_doc(dt, name)
                    if d.docstatus == 1:
                        d.cancel(); frappe.db.commit()
                    frappe.delete_doc(dt, name, force=True); frappe.db.commit()
                    print("CLEANED:", dt, name)
            print("FINAL_ALERT_EVENT:", frappe.db.count("Alert Event"))
            print("FINAL_IMPORT_CASE:", frappe.db.count("CB Import Case"))
            print("FINAL_BUDGET:", frappe.db.count("Material Budget"))
            print("FINAL_COMMIT:", frappe.db.count("Material Commitment"))
        except Exception as e:
            print("CLEANUP_ERR:", repr(e))
            import traceback
            traceback.print_exc()
    sys.exit(0)
main()
