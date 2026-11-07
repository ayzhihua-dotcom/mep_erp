import sys
def main():
    import frappe, inspect
    frappe.set_user("Administrator")
    for nm in ["Open Issues", "Overdue Issues", "Failed Scheduled Jobs"]:
        if frappe.db.exists("Number Card", nm):
            d = frappe.get_doc("Number Card", nm)
            print("CARD", nm, "| type:", d.type, "| function:", d.function, "| filters_json:", d.filters_json, "| doc:", d.document_type)
    print("--- OUR CARDS ---")
    for nm in ["缺料预警", "超预算预警", "逾期任务"]:
        d = frappe.get_doc("Number Card", nm)
        print("CARD", nm, "| filters_json:", d.filters_json)
    from frappe.desk.doctype.number_card import number_card
    try:
        print("GET_RESULT_SIG:", inspect.signature(number_card.get_result))
    except Exception as e:
        print("SIG_ERR", repr(e))
    src = inspect.getsource(number_card.get_result)
    print("=== get_result ===")
    print(src[:2200])
    sys.exit(0)
main()
