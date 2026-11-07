import sys
def main():
    import frappe
    frappe.set_user("Administrator")
    print("SE_DETAIL_HAS_PROJECT:", bool(frappe.get_meta("Stock Entry Detail").get_field("project")))
    print("SE_HEADER_HAS_PROJECT:", bool(frappe.get_meta("Stock Entry").get_field("project")))
    scripts = frappe.get_all("Server Script", filters={"name": ["like", "%IC02%"]}, fields=["name", "disabled", "reference_doctype", "doctype_event"])
    print("IC02_SCRIPTS:", scripts)
    for s in scripts:
        doc = frappe.get_doc("Server Script", s.name)
        body = (doc.script or "")
        print("=== SCRIPT:", s.name, "| disabled:", doc.disabled, "| ref:", doc.reference_doctype, "| event:", doc.doctype_event, "===")
        print(body[:1600])
        print("=== END ===")
    print("BIN_CB-GV-001:", frappe.db.get_value("Bin", {"item_code": "CB-GV-001", "warehouse": "巴西现场总仓 - 巴项"}, "actual_qty"))
    sys.exit(0)
main()
