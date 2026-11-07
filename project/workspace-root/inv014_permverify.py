def main():
    import frappe, sys
    out = []
    def w(*a):
        out.append(" ".join(str(x) for x in a))
    try:
        perm = frappe.db.sql("select role, permlevel, `read`, `write`, `create`, `delete` from `tabCustom DocPerm` where parent='Stock Settings'", as_dict=1)
        w("rows:", [dict(r) for r in perm])
        frappe.clear_cache(doctype="Stock Settings")
        frappe.clear_cache()
        w("cache cleared")
        hasperm = frappe.has_permission("Stock Settings", "read", user="dev01.sys@cb.local")
        w("dev01.sys read Stock Settings:", hasperm)
        w("RESULT: OK")
    except Exception as e:
        import traceback
        w("FATAL", repr(e))
        w(traceback.format_exc())
    finally:
        try:
            open("/home/frappe/inv014_out.txt", "w", encoding="utf-8").write("\n".join(out))
        except Exception:
            pass
    sys.exit(0)
main()
