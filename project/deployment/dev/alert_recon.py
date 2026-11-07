import sys
def main():
    import frappe
    frappe.set_user("Administrator")
    print("ALERT_RULE_COUNT:", frappe.db.count("Alert Rule"))
    for r in frappe.get_all("Alert Rule", fields=["name", "rule_code", "alert_type", "enabled", "assignee_role"]):
        print("RULE:", r.name, "|", r.alert_type, "| enabled:", r.enabled, "| role:", r.assignee_role)
    print("ALERT_EVENT_COUNT:", frappe.db.count("Alert Event"))
    print("--- MR gaps ---")
    for mr in frappe.get_all("Material Request", filters={"docstatus": 1}, fields=["name", "project"]):
        for it in frappe.get_all("Material Request Item", filters={"parent": mr.name}, fields=["item_code", "qty", "ordered_qty", "project"]):
            gap = (it.qty or 0) - (it.ordered_qty or 0)
            print("MR:", mr.name, "|", it.item_code, "| qty:", it.qty, "| ordered:", it.ordered_qty, "| gap:", gap, "| proj:", it.project or mr.project)
    print("--- import checklist ---")
    for c in frappe.get_all("CB Import Case", filters={"docstatus": 1}, fields=["name"]):
        und = frappe.get_all("CB Import Checklist", filters={"parent": c.name, "done": 0}, fields=["doc_name", "due_date"])
        print("CASE:", c.name, "| undone:", len(und))
    print("--- budget vs commit ---")
    for b in frappe.get_all("Material Budget", fields=["name", "project", "docstatus", "total_amount"]):
        cs = frappe.get_all("Material Commitment", filters={"project": b.project}, fields=["item_code", "qty_committed", "amount_committed", "docstatus"])
        print("BUDGET:", b.name, "|", b.project, "| ds:", b.docstatus, "| amt:", b.total_amount, "| commits:", [(c.item_code, c.qty_committed, c.amount_committed, c.docstatus) for c in cs])
    print("--- budget lines qty ---")
    for b in frappe.get_all("Material Budget", fields=["name", "project", "docstatus"]):
        for l in frappe.get_all("Material Budget Detail", filters={"parent": b.name}, fields=["item_code", "qty"]):
            print("BLINE:", b.name, "|", b.project, "| ds:", b.docstatus, "|", l.item_code, "| qty:", l.qty)
    sys.exit(0)
main()
