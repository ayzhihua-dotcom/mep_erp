import sys
def main():
    import frappe, json
    frappe.set_user("Administrator")
    cards = [
        {"label": "在办项目", "dt": "Project", "filters": [["status", "=", "Open"]]},
        {"label": "在办任务", "dt": "Task", "filters": [["status", "in", ["Open", "Working"]]]},
        {"label": "未关闭预警", "dt": "Alert Event", "filters": [["status", "!=", "已关闭"]]},
        {"label": "缺料预警", "dt": "Alert Event", "filters": [["alert_type", "=", "缺料"], ["status", "!=", "已关闭"]]},
        {"label": "超预算预警", "dt": "Alert Event", "filters": [["alert_type", "=", "超预算"], ["status", "!=", "已关闭"]]},
    ]
    for c in cards:
        if frappe.db.exists("Number Card", c["label"]):
            d = frappe.get_doc("Number Card", c["label"])
            d.type = "Document Type"
            d.document_type = c["dt"]
            d.function = "Count"
            d.is_public = 1
            d.filters_json = json.dumps(c["filters"], ensure_ascii=False)
            d.save(ignore_permissions=True)
            print("CARD_UPDATED:", c["label"])
        else:
            d = frappe.get_doc({
                "doctype": "Number Card",
                "label": c["label"],
                "type": "Document Type",
                "document_type": c["dt"],
                "function": "Count",
                "is_public": 1,
                "filters_json": json.dumps(c["filters"], ensure_ascii=False),
            })
            d.insert(ignore_permissions=True)
            print("CARD_CREATED:", d.name)
    frappe.db.commit()
    # attach to workspace
    ws = frappe.get_doc("Workspace", "CB 机电总控")
    have_nc = {r.number_card_name for r in ws.number_cards}
    labels = [c["label"] for c in cards]
    for lb in labels:
        if lb not in have_nc:
            ws.append("number_cards", {"number_card_name": lb, "label": lb})
    content = json.loads(ws.content or "[]")
    have_blocks = {b.get("data", {}).get("number_card_name") for b in content if b.get("type") == "number_card"}
    new_blocks = []
    for lb in labels:
        if lb not in have_blocks:
            new_blocks.append({"id": frappe.generate_hash(length=10), "type": "number_card", "data": {"number_card_name": lb, "col": 4}})
    ws.content = json.dumps(new_blocks + content, ensure_ascii=False)
    ws.save(ignore_permissions=True)
    frappe.db.commit()
    ws2 = frappe.get_doc("Workspace", "CB 机电总控")
    print("WS_NUMCARD_ROWS:", [r.number_card_name for r in ws2.number_cards])
    blocks = [b for b in json.loads(ws2.content or "[]") if b.get("type") == "number_card"]
    print("WS_CONTENT_NUMCARD_BLOCKS:", [b["data"]["number_card_name"] for b in blocks])
    # compute values
    from frappe.desk.doctype.number_card.number_card import get_result
    for c in cards:
        try:
            res = get_result(frappe.get_doc("Number Card", c["label"]))
            print("VALUE:", c["label"], "=", (res.get("value") if isinstance(res, dict) else res))
        except Exception as e:
            print("VALUE_ERR:", c["label"], repr(e))
    sys.exit(0)
main()
