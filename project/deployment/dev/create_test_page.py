import sys
def main():
    import frappe
    frappe.set_user("Administrator")
    name = "bulk-entry-test"
    if frappe.db.exists("Page", name):
        frappe.delete_doc("Page", name, force=True)
    d = frappe.get_doc({"doctype": "Page", "page_name": name, "title": "批量录入测试",
                        "module": "CB ERP", "standard": 0,
                        "page_html": "<div id='be'>nojs</div><script>document.getElementById('be').textContent='JS_OK';</script>"})
    d.insert(ignore_permissions=True)
    frappe.db.commit()
    print("PAGE_CREATED", d.name, "| standard:", d.standard)
    sys.exit(0)
main()
