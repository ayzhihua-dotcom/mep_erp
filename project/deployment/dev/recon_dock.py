import sys
def main():
    import frappe
    frappe.set_user("Administrator")
    dts = frappe.get_all("DocType", filters={"name": ["like", "%Dock%"]}, pluck="name")
    print("DOCK_DOCTYPES:", dts)
    for dt in dts:
        try:
            print(dt, "count:", frappe.db.count(dt))
            for r in frappe.get_all(dt, limit=5):
                print("  ROW:", r)
                d = frappe.get_doc(dt, r.name)
                print("  FIELDS:", {k: d.get(k) for k in (d.as_dict().keys()) if k not in ("doctype",) and not isinstance(d.get(k), list)})
                for f in d.meta.fields:
                    if f.fieldtype == "Table":
                        print("  TABLE", f.fieldname, "rows:", len(d.get(f.fieldname) or []))
        except Exception as e:
            print("ERR", dt, repr(e)[:150])
    sys.exit(0)
main()
