# -*- coding: utf-8 -*-
# S5 / TP-ALRBI-001 统一预警引擎
# 形态：Alert Event（统一对象）+ Alert Rule（规则主档）+ 本模块计算/去重/通知。
# 调度：hooks.scheduler_events cron 每 15 分钟（D-v5 代拟节拍草案）。
# 首批规则（任务书规则清单首批）：ALR-001 缺料、ALR-002 单证缺失、CST-007 超预算。
# 去重合并（任务书 §2.2，v1）：同类型+同关联对象+未关闭 → 更新度量值/计算时点，不新建；
# 同项目多对象合并为汇总预警（明细子行）留待 v2（本批如实登记为简化）。
# 通知：系统通知（Notification Log）+ Email（dev 无 SMTP，失败不阻断，登记）。
# 语言（UC-A05/D-11）：按责任人 User.language 取模板，缺省 zh。

import frappe
from frappe import _
from frappe.utils import now_datetime, today, getdate

RULE_VERSION_SEED = "v2026.11.05-1"

TEMPLATES = {
    "zh": {
        "subject": "【CB-ERP 预警】{title}",
        "body": "预警类型：{type}\n对象：{ref}\n摘要：{summary}\n度量值：{metric}\n责任人角色：{role}\n计算时点：{calc}\n（经预警引擎自动计算，规则版本 {ver}）",
    },
    "pt-BR": {
        "subject": "[CB-ERP Alerta] {title}",
        "body": "Tipo: {type}\nReferência: {ref}\nResumo: {summary}\nMétrica: {metric}\nResponsável: {role}\nCalculado em: {calc} (versão da regra {ver})",
    },
    "en": {
        "subject": "[CB-ERP Alert] {title}",
        "body": "Type: {type}\nReference: {ref}\nSummary: {summary}\nMetric: {metric}\nOwner: {role}\nComputed at: {calc} (rule {ver})",
    },
}

ALERT_TYPES_ZH = {
    "ALR-001": "缺料",
    "ALR-002": "单证缺失",
    "CST-007": "超预算",
    "PRJ-001": "任务逾期",
    "PRJ-002": "里程碑临期",
}


def run_all_rules():
    """调度入口 / 测试入口。每规则独立事务；失败不阻断他规则（捕获登记）。"""
    out = []
    rules = frappe.get_all("Alert Rule", filters={"enabled": 1},
                           fields=["name", "rule_code", "alert_type", "threshold_days",
                                   "assignee_role", "notify_email", "notify_system", "rule_version"])
    for rule in rules:
        handler = HANDLERS.get(rule.rule_code)
        if not handler:
            out.append("skip:{0}".format(rule.rule_code))
            continue
        try:
            findings = handler(rule) or []
            for f in findings:
                f["rule"] = rule
                _upsert(f)
                out.append("ok:{0}:{1}:{2}".format(rule.rule_code, f["ref_docname"], f.get("action", "")))
        except Exception as e:
            frappe.log_error("alert engine rule {0} failed: {1}".format(rule.rule_code, repr(e)[:400]),
                             "cb_erp.alerts")
            out.append("err:{0}:{1}".format(rule.rule_code, str(e)[:120]))
    return out


# ---------------------------------------------------------------- 兜底校验（UC-A03）

def validate_alert_event(doc, method=None):
    if doc.status == "已关闭":
        if not (doc.close_reason or "").strip():
            frappe.throw(_("关闭预警必须填写关闭原因"))
        if (doc.close_reason or "").strip().startswith("豁免") and not (doc.exemption_auth or "").strip():
            frappe.throw(_("豁免关闭必须填写豁免授权编号（IC-05 留痕）"))


@frappe.whitelist()
def close_alert(alert_name, reason, exemption_auth=None):
    """UC-A03：关闭需原因；豁免需授权留痕。"""
    a = frappe.get_doc("Alert Event", alert_name)
    a.status = "已关闭"
    a.close_reason = reason
    a.exemption_auth = exemption_auth
    a.save(ignore_permissions=True)
    frappe.db.commit()
    return a.name


# ---------------------------------------------------------------- 规则实现（首批三类）

def rule_material_gap(rule):
    """ALR-001 缺料：需求已批准（docstatus=1）未采购完 + 净缺口 > 0（TP-PRJ-004 口径，逐 MR 逐行）。"""
    findings = []
    for mr in frappe.get_all("Material Request", filters={"docstatus": 1},
                             fields=["name", "schedule_date", "custom_cb_project"]):
        rows = frappe.get_all("Material Request Item", filters={"parent": mr.name},
                              fields=["item_code", "qty", "ordered_qty", "project"])
        for r in rows:
            gap = (r.qty or 0) - (r.ordered_qty or 0)
            if gap > 0.001:
                findings.append({
                    "alert_type": "缺料",
                    "ref_doctype": "Material Request",
                    "ref_docname": mr.name,
                    "project": r.project or mr.custom_cb_project,
                    "item_code": r.item_code,
                    "metric_value": gap,
                    "severity": "警告",
                    "due_date": mr.schedule_date,
                    "summary": "缺料 {0}：净缺口 {1}（需求 {2}，已采购 {3}）".format(r.item_code, gap, r.qty, r.ordered_qty or 0),
                })
    return findings


def rule_doc_missing(rule):
    """ALR-002 单证缺失：进口案件已提交且清单行未完成（N 天停更判断 v1 简化：未完成即缺失，N 登记草案）。"""
    findings = []
    t = getdate(today())
    for case in frappe.get_all("CB Import Case", filters={"docstatus": 1}, fields=["name", "customs_status", "company"]):
        rows = frappe.get_all("CB Import Checklist", filters={"parent": case.name, "done": 0},
                              fields=["doc_name", "due_date", "holder_role"])
        if not rows:
            continue
        overdue = [r for r in rows if r.due_date and getdate(r.due_date) < t]
        findings.append({
            "alert_type": "单证缺失",
            "ref_doctype": "CB Import Case",
            "ref_docname": case.name,
            "metric_value": len(rows),
            "severity": "严重" if overdue else "警告",
            "due_date": min((r.due_date for r in rows if r.due_date), default=None),
            "summary": "单证缺失 {0} 项（{1}）：{2}".format(
                len(rows), case.name, "、".join(str(r.doc_name) for r in rows)),
        })
    return findings


def rule_over_budget(rule):
    """CST-007 超预算（数量口径，适配"只记数量不记金额"）：
    逐预算行（已提交）对比同项目同物料的已提交承诺数量；承诺数量 > 预算数量 → 超限，度量值=超出数量。"""
    findings = []
    for b in frappe.get_all("Material Budget", filters={"docstatus": 1},
                            fields=["name", "project"]):
        lines = frappe.get_all("Material Budget Detail", filters={"parent": b.name},
                               fields=["item_code", "qty"])
        for l in lines:
            committed = frappe.get_all("Material Commitment",
                                       filters={"docstatus": 1, "project": b.project, "item_code": l.item_code},
                                       fields=["qty_committed"])
            csum = sum(flt_safe(r.qty_committed) for r in committed)
            excess = frappe.utils.flt(csum - flt_safe(l.qty), 3)
            if excess > 0.001:
                findings.append({
                    "alert_type": "超预算",
                    "ref_doctype": "Material Budget",
                    "ref_docname": b.name,
                    "project": b.project,
                    "item_code": l.item_code,
                    "metric_value": excess,
                    "severity": "严重",
                    "summary": "项目 {0} 物料 {1} 承诺数量 {2} 超出预算数量 {3}，超 {4}".format(
                        b.project, l.item_code, csum, l.qty, excess),
                })
    return findings


def flt_safe(v):
    try:
        return float(v or 0)
    except Exception:
        return 0.0


def rule_task_overdue(rule):
    """PRJ-001 任务逾期：未完成/未取消且计划完成日 < 今天，度量值=逾期天数。"""
    findings = []
    t = getdate(today())
    for task in frappe.get_all("Task",
                               filters={"status": ["not in", ["Completed", "Cancelled"]]},
                               fields=["name", "subject", "project", "exp_end_date", "status"]):
        if not task.exp_end_date:
            continue
        end = getdate(task.exp_end_date)
        if end < t:
            days = (t - end).days
            findings.append({
                "alert_type": "其他",
                "ref_doctype": "Task",
                "ref_docname": task.name,
                "project": task.project,
                "metric_value": days,
                "severity": "严重" if days >= 7 else "警告",
                "due_date": task.exp_end_date,
                "summary": "任务逾期 {0} 天：{1}（计划完成 {2}，状态 {3}）".format(
                    days, task.subject, task.exp_end_date, task.status),
            })
    return findings


def rule_milestone_due(rule):
    """PRJ-002 里程碑临期：里程碑任务未完成且计划完成日在未来 N 天内（N=rule.threshold_days，默认7）。"""
    findings = []
    t = getdate(today())
    n = int(rule.threshold_days or 7)
    for task in frappe.get_all("Task",
                               filters={"is_milestone": 1, "status": ["not in", ["Completed", "Cancelled"]]},
                               fields=["name", "subject", "project", "exp_end_date", "status"]):
        if not task.exp_end_date:
            continue
        end = getdate(task.exp_end_date)
        days = (end - t).days
        if 0 <= days <= n:
            findings.append({
                "alert_type": "其他",
                "ref_doctype": "Task",
                "ref_docname": task.name,
                "project": task.project,
                "metric_value": days,
                "severity": "警告" if days > 3 else "严重",
                "due_date": task.exp_end_date,
                "summary": "里程碑临期 {0} 天：{1}（计划 {2}，状态 {3}）".format(
                    days, task.subject, task.exp_end_date, task.status),
            })
    return findings


HANDLERS = {
    "ALR-001": rule_material_gap,
    "ALR-002": rule_doc_missing,
    "CST-007": rule_over_budget,
    "PRJ-001": rule_task_overdue,
    "PRJ-002": rule_milestone_due,
}


# ---------------------------------------------------------------- 去重合并 + 通知

def _upsert(f):
    rule = f["rule"]
    key = "{0}:{1}:{2}".format(rule.rule_code, f["ref_doctype"], f["ref_docname"]) + \
          (":{0}".format(f["item_code"]) if f.get("item_code") else "")
    now = now_datetime()
    open_ev = frappe.get_all("Alert Event", filters={"dedupe_key": key, "status": ["!=", "已关闭"]},
                             fields=["name", "metric_value"], limit=1)
    notify_reason = None
    notify_reason_extra = None
    if open_ev:
        ev = frappe.get_doc("Alert Event", open_ev[0].name)
        old_metric = ev.metric_value
        ev.metric_value = f["metric_value"]
        ev.severity = f["severity"]
        ev.summary = f["summary"]
        ev.computed_at = now
        ev.rule_version = rule.rule_version or RULE_VERSION_SEED
        ev.due_date = f.get("due_date") or ev.due_date
        if frappe.utils.flt(old_metric, 4) != frappe.utils.flt(f["metric_value"], 4):
            notify_reason = "MetricChanged"
        ev.save(ignore_permissions=True)
        frappe.db.commit()
        f["action"] = "updated"
        f["event_name"] = ev.name
    else:
        ev = frappe.get_doc({
            "doctype": "Alert Event",
            "alert_type": f["alert_type"],
            "ref_doctype": f["ref_doctype"],
            "ref_docname": f["ref_docname"],
            "alert_summary": f["summary"],
            "project": f.get("project"),
            "item_code": f.get("item_code"),
            "metric_value": f["metric_value"],
            "severity": f["severity"],
            "assignee": _role_user(rule.assignee_role),
            "assignee_role": rule.assignee_role,
            "due_date": f.get("due_date"),
            "status": "待处理",
            "rule": rule.name,
            "rule_code": rule.rule_code,
            "dedupe_key": key,
            "computed_at": now,
            "rule_version": rule.rule_version or RULE_VERSION_SEED,
        })
        ev.insert(ignore_permissions=True)
        frappe.db.commit()
        f["action"] = "created"
        f["event_name"] = ev.name
        notify_reason = "New"
    if notify_reason:
        f["notify"] = _notify(rule, f, notify_reason)


def _role_user(role):
    if not role:
        return None
    for h in frappe.get_all("Has Role", filters={"role": role, "parenttype": "User"},
                            fields=["parent"], limit=30):
        u = frappe.get_value("User", h.parent, ["enabled", "user_type", "name"], as_dict=1)
        if u and u.enabled and u.user_type == "System User" and u.name not in ("Administrator", "Guest"):
            return u.name
    return None


def _notify(rule, f, reason):
    ev_name = f.get("event_name")
    user = None
    if ev_name:
        user = _role_user(rule.assignee_role) or frappe.get_value("Alert Event", ev_name, "assignee")
    if not user:
        return "no-assignee"
    lang = frappe.get_value("User", user, "language") or "zh"
    tpl = TEMPLATES.get(lang) or TEMPLATES["zh"]
    title = "{0}：{1}".format(ALERT_TYPES_ZH.get(rule.rule_code, rule.alert_type), (f["summary"] or "")[:60])
    ctx = {"title": title, "type": ALERT_TYPES_ZH.get(rule.rule_code, rule.alert_type),
           "ref": "{0} {1}".format(f["ref_doctype"], f["ref_docname"]),
           "summary": f["summary"], "metric": str(f["metric_value"]),
           "role": rule.assignee_role or "", "calc": str(now_datetime())[:19],
           "ver": rule.rule_version or RULE_VERSION_SEED}
    sent = []
    if rule.notify_system:
        nl = frappe.get_doc({
            "doctype": "Notification Log",
            "for_user": user,
            "type": "Alert",
            "subject": tpl["subject"].format(**ctx)[:140],
            "document_type": "Alert Event",
            "document_name": ev_name,
            "from_user": "Administrator",
        })
        nl.insert(ignore_permissions=True)
        sent.append("system:{0}".format(nl.name))
    if rule.notify_email:
        try:
            frappe.sendmail(recipients=[user], subject=tpl["subject"].format(**ctx),
                            message=tpl["body"].format(**ctx), retry=0)
            sent.append("email:queued")
        except Exception as e:
            sent.append("email:failed({0})".format(str(e)[:60]))
    frappe.db.set_value("Alert Event", ev_name, "notified", 1, update_modified=False)
    frappe.db.commit()
    return ";".join(sent)
