import sys
def main():
    import frappe
    frappe.set_user("Administrator")
    # 1) Project Kanban (按状态分组)
    kb_name = "项目看板"
    if frappe.db.exists("Kanban Board", kb_name):
        print("KANBAN_EXISTS:", kb_name)
    else:
        try:
            kb = frappe.get_doc({
                "doctype": "Kanban Board",
                "kanban_board_name": kb_name,
                "reference_doctype": "Project",
                "field_name": "status",
                "private": 0,
                "show_labels": 1,
            })
            kb.insert(ignore_permissions=True)
            frappe.db.commit()
            print("KANBAN_CREATED:", kb.name)
        except Exception as e:
            print("KANBAN_ERR:", repr(e))
    # 2) 把报告挂到 CB 机电总控 工作台（新增"项目视图"卡 + 报告链接）
    ws = frappe.get_doc("Workspace", "CB 机电总控")
    has_report = any((l.link_to == "项目物料执行台账") for l in ws.links)
    if has_report:
        print("WS_LINK_EXISTS: 项目物料执行台账")
    else:
        ws.append("links", {
            "type": "Card Break",
            "label": "项目视图",
        })
        ws.append("links", {
            "type": "Link",
            "label": "项目物料执行台账",
            "link_to": "项目物料执行台账",
            "link_type": "Report",
            "is_query_report": 1,
        })
        ws.save(ignore_permissions=True)
        frappe.db.commit()
        print("WS_LINK_ADDED: 项目视图 / 项目物料执行台账")
    ws2 = frappe.get_doc("Workspace", "CB 机电总控")
    print("WS_LINKS_COUNT:", len(ws2.links))
    for l in ws2.links:
        print("  LINK:", l.type, "|", l.label, "|", l.link_to, "|", l.link_type)
    sys.exit(0)
main()
