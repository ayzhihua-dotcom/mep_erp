import sys
def main():
    import frappe
    frappe.set_user("Administrator")
    DISC = "管道\n电气\n仪表\n暖通\n给排水\n消防\n钢结构\n机械设备\n焊接\n防腐保温\n安全环保\n其他"
    SYS = "工艺系统\n给排水系统\n消防系统\n暖通空调系统\n电气系统\n仪表自控系统\n弱电通信系统\n压缩空气系统\n蒸汽系统\n氮气系统\n其他"
    # 1) Bulk Entry fields
    dt = frappe.get_doc("DocType", "Bulk Entry")
    existing = {f.fieldname for f in dt.fields}
    added = []
    if "discipline" not in existing:
        dt.append("fields", {"fieldname": "discipline", "fieldtype": "Select", "label": "专业", "options": DISC, "in_list_view": 1}); added.append("discipline")
    if "system" not in existing:
        dt.append("fields", {"fieldname": "system", "fieldtype": "Select", "label": "系统", "options": SYS, "in_list_view": 1}); added.append("system")
    if "responsible" not in existing:
        dt.append("fields", {"fieldname": "responsible", "fieldtype": "Link", "label": "责任人", "options": "User", "in_list_view": 1}); added.append("responsible")
    if added:
        dt.save(ignore_permissions=True); frappe.db.commit(); print("BULK_ENTRY_FIELDS_ADDED:", added)
    else:
        print("BULK_ENTRY_FIELDS_EXIST")
    # 2) custom fields
    targets = ["Material Request", "Stock Entry", "Stock Reconciliation", "Purchase Order", "Material Budget",
               "Material Commitment", "CB Import Case", "CB Shipment", "Design BOM", "Design Change Request"]
    defs = [("custom_discipline", "Data", "专业", None), ("custom_system", "Data", "系统", None),
            ("custom_responsible", "Link", "责任人", "User")]
    made = 0
    for t in targets:
        for fn, ft, lb, opts in defs:
            if frappe.db.has_column(t, fn):
                continue
            try:
                d = {"doctype": "Custom Field", "dt": t, "fieldname": fn, "fieldtype": ft, "label": lb}
                if opts:
                    d["options"] = opts
                frappe.get_doc(d).insert(ignore_permissions=True)
                made += 1
            except Exception as e:
                print("CF_ERR", t, fn, repr(e)[:120])
    frappe.db.commit()
    print("CUSTOM_FIELDS_CREATED:", made)
    # 3) client script args
    cs = frappe.get_doc("Client Script", "Bulk Entry-Form")
    s = cs.script or ""
    old_args = "posting_date: frm.doc.posting_date },"
    new_args = "posting_date: frm.doc.posting_date, discipline: frm.doc.discipline, system: frm.doc.system, responsible: frm.doc.responsible },"
    if old_args in s:
        s = s.replace(old_args, new_args)
    old_fd = "        if (frm.doc.posting_date) fd.append('posting_date', frm.doc.posting_date);"
    if "fd.append('discipline'" not in s and old_fd in s:
        s = s.replace(old_fd, old_fd + "\n        if (frm.doc.discipline) fd.append('discipline', frm.doc.discipline);\n        if (frm.doc.system) fd.append('system', frm.doc.system);\n        if (frm.doc.responsible) fd.append('responsible', frm.doc.responsible);")
    cs.script = s
    cs.save(ignore_permissions=True)
    frappe.db.commit()
    print("CS_UPDATED has_disc_arg:", "discipline: frm.doc.discipline" in s, "| has_fd_disc:", "fd.append('discipline'" in s)
    frappe.clear_cache()
    sys.exit(0)
main()
