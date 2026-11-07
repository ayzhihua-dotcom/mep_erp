import frappe


def on_submit_change(doc, method=None):
    """设计变更审批（提交）后：按「变更明细」生成新版设计BOM（草稿），并回写生成结果。"""
    if doc.get("custom_generated_bom"):
        return
    items = doc.get("change_items") or []
    if not items:
        return
    if not doc.get("design_bom"):
        frappe.throw("设计变更未关联设计BOM，无法生成新版")

    old = frappe.get_doc("Design BOM", doc.design_bom)
    new = frappe.copy_doc(old)
    existing = {r.item_code: r for r in (new.get("bom_items") or [])}

    for ch in items:
        if not ch.item_code:
            continue
        if ch.item_code in existing:
            existing[ch.item_code].qty = ch.new_qty
        else:
            new.append("bom_items", {
                "item_code": ch.item_code,
                "item_name": ch.item_name,
                "qty": ch.new_qty,
                "uom": "个",
            })

    new.version_no = doc.get("new_version_no") or old.get("version_no")
    new.design_base = old.name
    new.amended_from = None
    # 新版BOM从「草稿」开始，避免把旧版的「已批准」工作流状态带入
    if new.get("workflow_state"):
        new.workflow_state = "草稿"
    new.docstatus = 0
    new.insert(ignore_permissions=True)

    doc.db_set("custom_generated_bom", new.name)
    frappe.msgprint("已按变更明细生成新版设计BOM：{0}".format(new.name))


def generate_for_change(change_name):
    """手动触发（便于脚本/按钮调用）。"""
    doc = frappe.get_doc("Design Change Request", change_name)
    on_submit_change(doc)
    frappe.db.commit()
    return doc.get("custom_generated_bom")


def run():
    """bench execute 入口：列出可生成/已生成的变更单。"""
    rows = frappe.get_all(
        "Design Change Request",
        fields=["name", "design_bom", "new_version_no", "workflow_state", "custom_generated_bom"],
        limit=0,
    )
    for r in rows:
        print(r.name, "|", r.design_bom, "|", r.new_version_no, "|", r.workflow_state, "| generated:", r.custom_generated_bom)
    return len(rows)
