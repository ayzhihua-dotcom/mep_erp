import sys
def main():
    import frappe
    try:
        fields = frappe.db.sql("select fieldname, fieldtype, hidden, read_only from tabDocField where parent='Website Settings' order by idx", as_dict=True)
        print("=== Website Settings fields ===")
        for f in fields:
            print(f.fieldname, f.fieldtype, "hidden" if f.hidden else "", "ro" if f.read_only else "")
        print("=== raw tabWebsite Settings row (setup_complete col?) ===")
        cols = [c[0] for c in frappe.db.sql("show columns from tabWebsite Settings")]
        print("COLUMNS:", [c for c in cols if 'setup' in c.lower() or 'complete' in c.lower()])
        print("ALL_COLS_SAMPLE:", cols[:20], "...total", len(cols))
        print("DONE:1")
    except Exception as e:
        print("ERR:", repr(e))
    sys.exit(0)
main()
