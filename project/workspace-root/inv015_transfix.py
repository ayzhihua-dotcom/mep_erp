def main():
    import frappe, sys
    out = []
    def w(*a):
        out.append(" ".join(str(x) for x in a))
    try:
        w("=== 补翻 zh 词条（DB Translation 路径）===")
        items = [
            ("Item", "物料"),
            ("Last Edited By", "最后编辑"),
            ("Sign In", "登录"),
            ("Welcome! Please sign in to continue.", "欢迎！请登录以继续。"),
            ("Forgot password?", "忘记密码？"),
        ]
        existing = frappe.get_all("Translation", filters={"language": "zh"}, fields=["name", "source_text"])
        have = {r.get("source_text") for r in existing}
        w("existing zh rows:", len(existing))
        added = []
        for src, dst in items:
            if src in have:
                w("skip (exists):", src)
                continue
            frappe.get_doc({"doctype": "Translation", "language": "zh", "source_text": src, "translated_text": dst}).insert()
            added.append(src)
        frappe.db.commit()
        w("added:", added)
        frappe.clear_cache()
        frappe.local.lang = "zh"
        for src, dst in items:
            got = frappe._(src)
            w("check", repr(src), "->", got, "OK" if got == dst else "STILL-EN")
        w("RESULT: OK")
    except Exception as e:
        import traceback
        w("FATAL", repr(e))
        w(traceback.format_exc())
    finally:
        try:
            open("/home/frappe/inv015_out.txt", "w", encoding="utf-8").write("\n".join(out))
        except Exception:
            pass
    sys.exit(0)
main()
