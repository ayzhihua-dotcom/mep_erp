def main():
    import frappe, sys, json
    out = []
    def w(*a):
        out.append(" ".join(str(x) for x in a))
    try:
        w("=== 全中文落地快速核查（只核可客观验证项）===")
        sys_set = frappe.get_doc("System Settings")
        w("System Settings.language:", sys_set.get("language"))
        langs = frappe.db.sql("select language, count(*) as c from `tabUser` where ifnull(enabled,0)=1 group by language", as_dict=1)
        w("enabled users by language:", [(r.get("language"), r.c) for r in langs])
        tr_all = frappe.get_all("Translation", filters={"language": "zh"}, fields=["*"])
        w("zh Translation rows total:", len(tr_all))
        samples = ("Stock Entry", "Material Receipt", "Material Issue", "Material Transfer", "Quality Inspection", "Submit", "Draft", "Warehouse")
        got = {}
        for row in tr_all:
            st = row.get("source_text")
            if st in samples and st not in got:
                got[st] = row.get("translated_text") if "translated_text" in row else row.get("translated")
        w("sample translations found:", got)
        missed = [s for s in samples if s not in got]
        w("samples missed in zh DB:", missed)
        w("--- Server Scripts inventory (Stock Entry events) ---")
        sss = frappe.get_all("Server Script", filters={"reference_doctype": "Stock Entry"}, fields=["name", "doctype_event", "enabled"], order_by="name")
        for s in sss:
            w("  SS", s.name, "|", s.doctype_event, "| enabled", s.enabled)
        w("--- doc事件 hook（Python hooks.py 无 Stock Entry 事件）已另登记，此处复核 enabled 汇总 ---")
        w("SE-related SS count:", len(sss), " enabled:", sum(1 for s in sss if s.enabled))
        w("RESULT:", "OK")
    except Exception as e:
        import traceback
        w("FATAL", repr(e))
        w(traceback.format_exc())
    finally:
        try:
            open("/home/frappe/inv011_out.txt", "w", encoding="utf-8").write("\n".join(out))
        except Exception:
            pass
    sys.exit(0)
main()
