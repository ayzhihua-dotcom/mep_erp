# -*- coding: utf-8 -*-
# 全量模拟数据播种器（演示/压测用）
# 分阶段：seed_master -> seed_docs -> seed_stock -> run_alerts
import random
import frappe
from frappe.utils import today, add_days, nowdate

COMPANY = "中巴机电（巴西）项目有限公司"
WH = "巴西现场总仓 - 巴项"
GROUPS = ["管道阀门", "电缆电气", "仪表自控", "机电主材"]
PREFIX = {"管道阀门": "PV", "电缆电气": "EL", "仪表自控": "IN", "机电主材": "ME"}
SUPPLIER_GROUP = "中国供应商"
PROJ_NS = "PROJ-.####"


def _uom():
    uoms = frappe.get_all("UOM", pluck="name")
    for cand in ("Nos", "Pcs", "件", "个", "套", "米"):
        if cand in uoms:
            return cand
    return uoms[0]


def _sim_items():
    d = {}
    for g in GROUPS:
        d[g] = frappe.get_all("Item", filters={"item_code": ["like", "SIM-%s-%%" % PREFIX[g]]},
                              fields=["item_code", "valuation_rate"], order_by="item_code")
    return d


def seed_master(n_items=1000, n_sup=50, n_proj=50, n_eng=50):
    frappe.set_user("Administrator")
    uom = _uom()
    per = n_items // len(GROUPS)
    made = 0
    for g in GROUPS:
        for i in range(1, per + 1):
            code = "SIM-%s-%04d" % (PREFIX[g], i)
            if frappe.db.exists("Item", code):
                continue
            d = frappe.get_doc({
                "doctype": "Item", "item_code": code,
                "item_name": "模拟%s-%04d" % (g, i),
                "item_group": g, "stock_uom": uom, "is_stock_item": 1,
                "valuation_rate": random.randint(10, 5000),
                "custom_qc_required": 0,
                "description": "模拟数据（%s专业）" % g,
            })
            d.insert(ignore_permissions=True)
            made += 1
            if made % 100 == 0:
                frappe.db.commit()
                print("items_done", made)
    frappe.db.commit()
    print("ITEM_SIM_COUNT", frappe.db.count("Item", {"item_code": ["like", "SIM-%"]}))

    for i in range(1, n_sup + 1):
        nm = "模拟供应商-%02d" % i
        if frappe.db.exists("Supplier", {"supplier_name": nm}):
            continue
        frappe.get_doc({"doctype": "Supplier", "supplier_name": nm, "supplier_type": "Company",
                        "supplier_group": SUPPLIER_GROUP}).insert(ignore_permissions=True)
    frappe.db.commit()
    print("SUPPLIER_SIM_COUNT", frappe.db.count("Supplier", {"supplier_name": ["like", "模拟供应商-%"]}))

    for i in range(1, n_proj + 1):
        nm = "模拟项目-%02d" % i
        if frappe.db.exists("Project", {"project_name": nm}):
            continue
        start = add_days(today(), -60 + (i % 30))
        end = add_days(today(), 120 + (i % 60))
        frappe.get_doc({"doctype": "Project", "project_name": nm, "company": COMPANY,
                        "naming_series": PROJ_NS, "status": "Open",
                        "expected_start_date": start, "expected_end_date": end,
                        "percent_complete_method": "Task Progress"}).insert(ignore_permissions=True)
    frappe.db.commit()
    print("PROJECT_SIM_COUNT", frappe.db.count("Project", {"project_name": ["like", "模拟项目-%"]}))

    for i in range(1, n_eng + 1):
        email = "eng%02d@cb.local" % i
        if frappe.db.exists("User", email):
            continue
        frappe.get_doc({"doctype": "User", "email": email, "first_name": "工程师%02d" % i,
                        "user_type": "System User", "enabled": 1,
                        "roles": [{"role": "ENG 工程人员"}]}).insert(ignore_permissions=True)
    frappe.db.commit()
    print("ENG_USER_COUNT", frappe.db.count("User", {"email": ["like", "eng%@cb.local"]}))
    return "MASTER_DONE items=%s suppliers=%s projects=%s engineers=%s" % (
        frappe.db.count("Item"), frappe.db.count("Supplier"),
        frappe.db.count("Project"), frappe.db.count("User"))


def seed_docs():
    frappe.set_user("Administrator")
    uom = _uom()
    sim = _sim_items()
    projects = frappe.get_all("Project", filters={"project_name": ["like", "模拟项目-%"]},
                              fields=["name", "project_name", "expected_start_date"], order_by="name")
    suppliers = frappe.get_all("Supplier", filters={"supplier_name": ["like", "模拟供应商-%"]},
                               pluck="name", order_by="name")
    stats = {"budget": 0, "commit": 0, "mr": 0, "po": 0, "ic": 0, "shp": 0, "task": 0, "err": 0}
    for idx, p in enumerate(projects):
        try:
            if frappe.db.exists("Material Budget", {"project": p.name}):
                continue
            g = GROUPS[idx % len(GROUPS)]
            items = sim.get(g) or []
            if not items:
                continue
            chosen = items[:10]
            lines = []
            total = 0
            for it in chosen:
                qty = random.randint(10, 100)
                rate = it.valuation_rate or 100
                amt = qty * rate
                total += amt
                lines.append({"item_code": it.item_code, "qty": qty, "uom": uom, "rate": rate, "amount": amt})
            b = frappe.get_doc({"doctype": "Material Budget", "company": COMPANY, "project": p.name,
                                "budget_items": lines, "total_amount": total})
            b.insert(ignore_permissions=True)
            b.submit()
            frappe.db.commit()
            stats["budget"] += 1
            # commitments: first over budget -> CST-007
            for j in range(min(2, len(lines))):
                ln = lines[j]
                q = ln["qty"] + (10 if j == 0 else 0)
                c = frappe.get_doc({"doctype": "Material Commitment", "company": COMPANY, "project": p.name,
                                    "budget": b.name, "item_code": ln["item_code"], "qty_committed": q,
                                    "rate": ln["rate"], "amount_committed": q * ln["rate"],
                                    "snapshot_date": nowdate()})
                c.insert(ignore_permissions=True)
                c.submit()
                stats["commit"] += 1
            frappe.db.commit()
            # MR (engineer) with gap
            eng = "eng%02d@cb.local" % ((idx % 50) + 1)
            mr = frappe.get_doc({"doctype": "Material Request", "material_request_type": "Purchase",
                                 "company": COMPANY, "custom_cb_project": p.name,
                                 "schedule_date": add_days(today(), 7),
                                 "items": [{"item_code": ln2["item_code"], "qty": ln2["qty"],
                                            "schedule_date": add_days(today(), 7)} for ln2 in lines[:3]]})
            mr.insert(ignore_permissions=True)
            mr.submit()
            frappe.db.set_value("Material Request", mr.name, "owner", eng, update_modified=False)
            stats["mr"] += 1
            frappe.db.commit()
            # PO (IC-01: budget link + total <= budget)
            supplier = suppliers[idx % len(suppliers)] if suppliers else None
            po_items = []
            po_total = 0
            for ln in lines[:2]:
                q = min(ln["qty"], 5)
                amt = q * ln["rate"]
                po_total += amt
                po_items.append({"item_code": ln["item_code"], "qty": q, "rate": ln["rate"],
                                 "amount": amt, "schedule_date": add_days(today(), 10)})
            po = frappe.get_doc({"doctype": "Purchase Order", "company": COMPANY, "supplier": supplier,
                                 "custom_cb_project": p.name, "custom_cb_budget": b.name,
                                 "transaction_date": today(), "schedule_date": add_days(today(), 10),
                                 "currency": frappe.db.get_value("Company", COMPANY, "default_currency"),
                                 "conversion_rate": 1, "items": po_items})
            po.insert(ignore_permissions=True)
            po.submit()
            stats["po"] += 1
            frappe.db.commit()
            # import case + undone checklist -> ALR-002
            ic = frappe.get_doc({"doctype": "CB Import Case", "company": COMPANY, "purchase_order": po.name,
                                 "customs_status": "单证准备",
                                 "checklists": [
                                     {"doc_name": "提单", "done": 0, "due_date": add_days(today(), -5)},
                                     {"doc_name": "发票", "done": 0, "due_date": add_days(today(), 3)},
                                     {"doc_name": "箱单", "done": 1, "due_date": add_days(today(), -1)},
                                 ]})
            ic.insert(ignore_permissions=True)
            ic.submit()
            stats["ic"] += 1
            frappe.db.commit()
            # shipment
            sh = frappe.get_doc({"doctype": "CB Shipment", "company": COMPANY, "purchase_order": po.name,
                                 "shipment_status": "在途", "carrier": "模拟承运商",
                                 "tracking_no": "SIM-TRK-%03d" % idx,
                                 "etd": add_days(today(), -10), "eta": add_days(today(), 20)})
            sh.insert(ignore_permissions=True)
            sh.submit()
            stats["shp"] += 1
            frappe.db.commit()
            # tasks (1 overdue -> PRJ-001, 1 near milestone -> PRJ-002, 3 future)
            pstart = p.expected_start_date
            for k in range(5):
                subj = "模拟任务-%02d-%d" % (idx + 1, k + 1)
                if frappe.db.exists("Task", {"subject": subj, "project": p.name}):
                    continue
                if k == 0:
                    s_d, e_d, ms, st = pstart, add_days(today(), -2), 0, "Working"
                elif k == 1:
                    s_d, e_d, ms, st = add_days(today(), -1), add_days(today(), 3), 1, "Open"
                else:
                    s_d, e_d, ms, st = add_days(today(), 5 * k), add_days(today(), 5 * k + 10), 0, "Open"
                frappe.get_doc({"doctype": "Task", "subject": subj, "project": p.name,
                                "status": st, "priority": "Medium", "progress": random.randint(0, 100),
                                "is_milestone": ms, "exp_start_date": s_d + " 09:00:00" if isinstance(s_d, str) else str(s_d) + " 09:00:00",
                                "exp_end_date": e_d + " 18:00:00" if isinstance(e_d, str) else str(e_d) + " 18:00:00"}).insert(ignore_permissions=True)
                stats["task"] += 1
            frappe.db.commit()
        except Exception as e:
            stats["err"] += 1
            frappe.db.rollback()
            print("PROJ_ERR", p.name, repr(e)[:300])
    print("STATS", stats)
    return "DOCS_DONE " + str(stats)


def seed_stock(n=10):
    frappe.set_user("Administrator")
    uom = _uom()
    sim = _sim_items()
    projects = frappe.get_all("Project", filters={"project_name": ["like", "模拟项目-%"]},
                              fields=["name"], order_by="name", limit=n)
    items = sim.get(GROUPS[0]) or []
    made = 0
    for idx, p in enumerate(projects):
        it = items[idx % len(items)]
        rate = it.valuation_rate or 100
        try:
            se = frappe.get_doc({"doctype": "Stock Entry", "stock_entry_type": "Material Receipt",
                                 "company": COMPANY,
                                 "items": [{"item_code": it.item_code, "qty": 500, "t_warehouse": WH,
                                            "basic_rate": rate, "uom": uom}]})
            se.insert(ignore_permissions=True)
            se.submit()
            frappe.db.commit()
            se2 = frappe.get_doc({"doctype": "Stock Entry", "stock_entry_type": "Material Issue",
                                  "company": COMPANY, "project": p.name,
                                  "items": [{"item_code": it.item_code, "qty": 10, "s_warehouse": WH,
                                             "basic_rate": rate, "uom": uom, "project": p.name}]})
            se2.insert(ignore_permissions=True)
            se2.submit()
            frappe.db.commit()
            made += 1
        except Exception as e:
            frappe.db.rollback()
            print("STOCK_ERR", p.name, repr(e)[:300])
    print("STOCK_PROJECTS_DONE", made)
    return "STOCK_DONE %s" % made


def run_alerts():
    frappe.set_user("Administrator")
    from cb_erp.cb_erp.alerts import run_all_rules
    out = run_all_rules()
    print("ALERT_RUN", out[:20], "...total", len(out))
    return "ALERTS_DONE events=%s" % frappe.db.count("Alert Event")


def seed_extra():
    frappe.set_user("Administrator")
    uom = _uom()
    sim = _sim_items()
    projects = frappe.get_all("Project", filters={"project_name": ["like", "模拟项目-%"]},
                              fields=["name"], order_by="name")
    made = {"bom": 0, "dcr": 0, "qi": 0, "err": 0}
    boms = []
    for idx, p in enumerate(projects):
        g = GROUPS[idx % len(GROUPS)]
        items = (sim.get(g) or [])[:5]
        ex = frappe.get_all("Design BOM", filters={"project": p.name}, fields=["name"], limit=1)
        if ex:
            boms.append(ex[0].name)
            continue
        if not items:
            boms.append(None)
            continue
        try:
            bom_items = [{"item_code": it.item_code, "item_name": "模拟" + it.item_code,
                          "qty": random.randint(5, 50), "uom": uom} for it in items]
            d = frappe.get_doc({"doctype": "Design BOM", "project": p.name, "company": COMPANY,
                                "version_no": "V1.0",
                                "professional": (g if g in ("管道阀门", "电缆电气", "仪表自控") else "其他"),
                                "bom_items": bom_items})
            d.insert(ignore_permissions=True)
            d.submit()
            frappe.db.commit()
            made["bom"] += 1
            boms.append(d.name)
        except Exception as e:
            made["err"] += 1
            frappe.db.rollback()
            boms.append(None)
            print("BOM_ERR", p.name, repr(e)[:200])
    for b in [x for x in boms if x][:20]:
        try:
            d = frappe.get_doc({"doctype": "Design Change Request", "design_bom": b,
                                "reason": "现场调整", "new_version_no": "V1.1",
                                "change_content": "模拟变更：管径/线径调整（演示）",
                                "impact_assessment": "影响物料与工期（模拟）"})
            d.insert(ignore_permissions=True)
            d.submit()
            frappe.db.commit()
            made["dcr"] += 1
        except Exception as e:
            made["err"] += 1
            frappe.db.rollback()
            print("DCR_ERR", b, repr(e)[:200])
    ses = frappe.get_all("Stock Entry", filters={"docstatus": 1, "purpose": "Material Receipt"},
                         fields=["name", "company"], limit=10)
    for se in ses:
        try:
            if frappe.db.exists("Quality Inspection", {"reference_type": "Stock Entry", "reference_name": se.name}):
                continue
            sed = frappe.get_all("Stock Entry Detail", filters={"parent": se.name}, fields=["item_code"], limit=1)
            if not sed:
                continue
            q = frappe.get_doc({"doctype": "Quality Inspection", "inspection_type": "Incoming",
                                "company": se.company, "reference_type": "Stock Entry",
                                "reference_name": se.name, "item_code": sed[0].item_code,
                                "sample_size": 5, "status": "Accepted",
                                "inspected_by": "Administrator", "report_date": today()})
            q.insert(ignore_permissions=True)
            q.submit()
            frappe.db.commit()
            made["qi"] += 1
        except Exception as e:
            made["err"] += 1
            frappe.db.rollback()
            print("QI_ERR", se.name, repr(e)[:200])
    print("EXTRA", made)
    return "EXTRA_DONE " + str(made)


def status():
    frappe.set_user("Administrator")
    return {
        "items": frappe.db.count("Item"),
        "suppliers": frappe.db.count("Supplier"),
        "projects": frappe.db.count("Project"),
        "engineers": frappe.db.count("User", {"email": ["like", "eng%@cb.local"]}),
        "budgets": frappe.db.count("Material Budget"),
        "commitments": frappe.db.count("Material Commitment"),
        "mrs": frappe.db.count("Material Request"),
        "pos": frappe.db.count("Purchase Order"),
        "import_cases": frappe.db.count("CB Import Case"),
        "shipments": frappe.db.count("CB Shipment"),
        "tasks": frappe.db.count("Task"),
        "stock_entries": frappe.db.count("Stock Entry"),
        "alert_events": frappe.db.count("Alert Event"),
        "sle": frappe.db.count("Stock Ledger Entry"),
    }
