import sys
def main():
    import frappe
    frappe.set_user("Administrator")
    mri = [f.fieldname for f in frappe.get_meta("Material Request Item").fields]
    mrh = [f.fieldname for f in frappe.get_meta("Material Request").fields]
    print("MRI_HAS_project:", "project" in mri, "| MRI_HAS_custom_cb_project:", "custom_cb_project" in mri)
    print("MR_HEADER_LINKPROJ:", [f.fieldname for f in frappe.get_meta("Material Request").fields if f.fieldtype == "Link" and f.options == "Project"])
    print("MR_HEADER_has_project:", "project" in mrh)
    for mr in frappe.get_all("Material Request", fields=["name", "docstatus", "custom_cb_project"]):
        print("MR:", mr.name, "| ds:", mr.docstatus, "| custom_cb_project:", mr.custom_cb_project)
        for it in frappe.get_all("Material Request Item", filters={"parent": mr.name}, fields=["item_code", "qty", "ordered_qty"]):
            print("   MRI:", it.item_code, "| qty:", it.qty, "| ordered:", it.ordered_qty)
    for c in frappe.get_all("CB Import Case", fields=["name", "docstatus", "customs_status"]):
        print("CASE:", c.name, "| ds:", c.docstatus, "| customs:", c.customs_status)
        for r in frappe.get_all("CB Import Checklist", filters={"parent": c.name}, fields=["doc_name", "done", "due_date"]):
            print("   CHK:", r.doc_name, "| done:", r.done, "| due:", r.due_date)
    for b in frappe.get_all("Material Budget", fields=["name", "project", "docstatus", "total_amount"]):
        print("BUDGET:", b.name, "| proj:", b.project, "| ds:", b.docstatus, "| amt:", b.total_amount)
        for l in frappe.get_all("Material Budget Detail", filters={"parent": b.name}, fields=["item_code", "qty"]):
            print("   BLINE:", l.item_code, "| qty:", l.qty)
    for c in frappe.get_all("Material Commitment", fields=["name", "project", "item_code", "qty_committed", "amount_committed", "docstatus"]):
        print("COMMIT:", c.name, "| proj:", c.project, "|", c.item_code, "| qty:", c.qty_committed, "| amt:", c.amount_committed, "| ds:", c.docstatus)
    sys.exit(0)
main()
