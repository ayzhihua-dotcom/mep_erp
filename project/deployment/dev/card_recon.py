import sys
def main():
    import frappe
    frappe.set_user("Administrator")
    wm = frappe.get_meta("Workspace")
    print("WS_FIELDS:", [(f.fieldname, f.fieldtype, (f.options if f.fieldtype == "Table" else "")) for f in wm.fields if f.fieldname in ("content", "number_cards", "charts", "links", "shortcuts", "quick_lists")])
    sw = frappe.get_doc("Workspace", "Stock")
    print("STOCK_NUMCARDS_ROWS:", [(nr.as_dict() if hasattr(nr, "as_dict") else nr) for nr in sw.number_cards])
    # content number_card blocks
    import json
    try:
        content = json.loads(sw.content or "[]")
        nc_blocks = [c for c in content if c.get("type") == "number_card"]
        print("STOCK_CONTENT_NUMCARD_BLOCKS:", nc_blocks[:3])
    except Exception as e:
        print("CONTENT_ERR:", repr(e))
    ncm = frappe.get_meta("Number Card")
    print("NUMBER_CARD_FIELDS:", [(f.fieldname, f.fieldtype) for f in ncm.fields])
    print("EXISTING_NUMCARDS:", frappe.get_all("Number Card", fields=["name", "label", "document_type", "function"], limit=10))
    sys.exit(0)
main()
