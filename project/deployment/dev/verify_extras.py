import sys
def main():
    import frappe
    frappe.set_user("Administrator")
    cs = frappe.get_doc("Client Script", "Bulk Entry-Form")
    print("CS_AUTOFILL:", "d.get_value('item_code')" in (cs.script or ""))
    print("PRINT_FORMATS:", frappe.get_all("Print Format", filters={"name": ["like", "物料明细九列%"]}, pluck="name"))
    from frappe.desk.query_report import run
    try:
        res = run("物料明细（九列）", filters={})
        print("REPORT_ROWS:", len(res.get("result") or []))
        print("REPORT_COLS:", [c.get("label") for c in (res.get("columns") or [])])
        for r in (res.get("result") or [])[:3]:
            print("ROW:", r)
    except Exception as e:
        print("REPORT_ERR:", repr(e))
    sys.exit(0)
main()
