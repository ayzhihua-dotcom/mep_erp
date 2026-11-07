import sys
def main():
    import frappe
    frappe.set_user("Administrator")
    rows = frappe.db.sql("""select parent, idx, link_type, link_to, title, icon, hidden from `tabDock Item`
                            where parent in ('frappe','erpnext') order by parent, idx""", as_dict=True)
    for r in rows:
        print(r["parent"], r["idx"], r["link_type"], r["link_to"], "|", r["title"], "|", r["icon"], "|hidden", r["hidden"])
    print("COUNT:", len(rows))
    # check raw dock docs meta modified
    for a in ("frappe", "erpnext"):
        d = frappe.get_doc("Dock", a)
        print(a, "modified", d.modified, "items", len(d.items))
    sys.exit(0)
main()
