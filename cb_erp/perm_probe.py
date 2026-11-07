# -*- coding: utf-8 -*-
import json
def run():
    import frappe
    frappe.set_user("Administrator")
    print("BUDGET_PERMS:", json.dumps([{k: r.get(k) for k in ("role","read","write","create","report","export","delete","submit","cancel","amend")}
                                       for r in frappe.get_all("Custom DocPerm", filters={"parent": "Material Budget"},
                                                                fields=["role","read","write","create","report","export","delete","submit","cancel","amend"])], ensure_ascii=True))
    print("CD_PERMS:", frappe.db.count("Custom DocPerm", {"parent": "CB Discipline"}))
    print("CS_PERMS:", frappe.db.count("Custom DocPerm", {"parent": "CB System"}))
    print("ROLES:", json.dumps([r.name for r in frappe.get_all("Role", fields=["name"], limit=0)], ensure_ascii=True)[:1200])
    return "OK"
