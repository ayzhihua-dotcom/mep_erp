def main():
    import frappe, sys
    out = []
    def w(*a):
        out.append(" ".join(str(x) for x in a))
    try:
        w("=== 运行时翻译核查（CSV 加载路径）===")
        frappe.local.lang = "zh"
        samples = ["Stock Entry", "Material Receipt", "Material Transfer", "Quality Inspection", "Warehouse", "Submit", "Draft"]
        try:
            from frappe.translate import get_translation
            for s in samples:
                try:
                    w("  tr", s, "->", get_translation("zh").translate(s))
                except Exception as e:
                    w("  tr", s, "ERR", repr(e))
        except Exception as e:
            w("get_translation import err:", repr(e))
        w("--- fallback frappe._ ---")
        for s in samples:
            try:
                w("  _ ", s, "->", frappe._(s))
            except Exception as e:
                w("  _ ", s, "ERR", repr(e))
        w("=== Server Script 列名与清单 ===")
        cols = frappe.db.sql("show columns from `tabServer Script`", as_dict=1)
        w("columns:", [r.get("Field") for r in cols])
        colnames = set(r.get("Field") for r in cols)
        fields = [f for f in ["name", "doctype_event", "reference_doctype", "enabled", "disabled"] if f in colnames]
        sss = frappe.get_all("Server Script", filters={"reference_doctype": "Stock Entry"}, fields=fields, order_by="name")
        for s in sss:
            w("  SS", {k: s.get(k) for k in sss[0].keys()} if sss else s)
        w("SS count:", len(sss))
        w("=== language=None 的 2 个用户 ===")
        for r in frappe.db.sql("select name, language, enabled from `tabUser` where language is null", as_dict=1):
            w("  user", r.get("name"), "enabled", r.get("enabled"))
        w("RESULT:", "OK")
    except Exception as e:
        import traceback
        w("FATAL", repr(e))
        w(traceback.format_exc())
    finally:
        try:
            open("/home/frappe/inv012_out.txt", "w", encoding="utf-8").write("\n".join(out))
        except Exception:
            pass
    sys.exit(0)
main()
