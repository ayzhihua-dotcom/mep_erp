def main():
    import frappe, sys
    out = []
    def w(*a):
        out.append(" ".join(str(x) for x in a))
    try:
        w("=== fix: Custom DocPerm Stock Settings -> System Manager ===")
        exists = frappe.db.exists("Custom DocPerm", {"parent": "Stock Settings", "role": "System Manager"})
        w("existing custom perm:", exists)
        if not exists:
            frappe.get_doc({
                "doctype": "Custom DocPerm",
                "parent": "Stock Settings",
                "parenttype": "DocType",
                "parentfield": "permissions",
                "role": "System Manager",
                "permlevel": 0,
                "read": 1,
                "write": 1,
                "create": 0,
                "delete": 0,
            }).insert(ignore_if_duplicate=True)
            frappe.db.commit()
            w("inserted Custom DocPerm")
        else:
            w("already present, no-op")
        perm = frappe.db.sql("select role, permlevel, read, write, create, `delete` from `tabCustom DocPerm` where parent='Stock Settings'", as_dict=1)
        w("rows:", [dict(r) for r in perm])
        frappe.clear_cache(doctype="Stock Settings")
        frappe.clear_cache()
        w("cache cleared")
        w("RESULT: OK")
    except Exception as e:
        import traceback
        w("FATAL", repr(e))
        w(traceback.format_exc())
    finally:
        try:
            open("/home/frappe/inv013_out.txt", "w", encoding="utf-8").write("\n".join(out))
        except Exception:
            pass
    sys.exit(0)
main()
