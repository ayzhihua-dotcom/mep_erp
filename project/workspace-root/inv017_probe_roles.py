def main():
    import frappe, sys
    out = []
    def w(*a):
        out.append(" ".join(str(x) for x in a))
    try:
        w("all non-standard roles in site:")
        for r in frappe.db.sql("select name from `tabRole` where not disabled order by name", as_dict=1):
            w(" ", r.name)
        w("roles of dev01.sys@cb.local (super-ish reference):")
        for r in frappe.db.sql("select role from `tabHas Role` where parent='dev01.sys@cb.local' and parenttype='User'", as_dict=1):
            w(" ", r.role)
        w("usuarios chenzhihua exists:", bool(frappe.db.exists("User", "chenzhihua@cb.local")))
        w("RESULT: OK (probe only)")
    except Exception as e:
        import traceback
        w("FATAL", repr(e))
        w(traceback.format_exc())
    finally:
        try:
            open("/home/frappe/inv017_out.txt", "w", encoding="utf-8").write("\n".join(out))
        except Exception:
            pass
    sys.exit(0)
main()
