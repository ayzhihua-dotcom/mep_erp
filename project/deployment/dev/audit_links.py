import sys
def main():
    import frappe
    frappe.set_user("Administrator")
    c = frappe.db.count
    print("=== 主数据 ===")
    print("ITEM", c("Item"), "| ITEM_GROUP", c("Item Group"))
    print("ITEMS_ON_GROUP_NODES:", frappe.db.sql("select count(*) c from `tabItem` i join `tabItem Group` ig on ig.name=i.item_group where ig.is_group=1", as_dict=True))
    print("=== 项目链 ===")
    print("BUDGET total", c("Material Budget"), "| with_project", c("Material Budget", {"project": ["is", "set"]}))
    print("COMMIT total", c("Material Commitment"), "| proj", c("Material Commitment", {"project": ["is", "set"]}),
          "| budget", c("Material Commitment", {"budget": ["is", "set"]}), "| po", c("Material Commitment", {"po": ["is", "set"]}))
    print("MR total", c("Material Request"), "| proj", c("Material Request", {"custom_cb_project": ["is", "set"]}))
    print("PO total", c("Purchase Order"), "| proj", c("Purchase Order", {"custom_cb_project": ["is", "set"]}),
          "| budget", c("Purchase Order", {"custom_cb_budget": ["is", "set"]}))
    print("IMPORT total", c("CB Import Case"), "| po", c("CB Import Case", {"purchase_order": ["is", "set"]}))
    print("SHIP total", c("CB Shipment"), "| po", c("CB Shipment", {"purchase_order": ["is", "set"]}))
    print("=== 库存 ===")
    print("SE total", c("Stock Entry"), "| receipt", c("Stock Entry", {"purpose": "Material Receipt"}),
          "| issue", c("Stock Entry", {"purpose": "Material Issue"}))
    print("ISSUE with_project", c("Stock Entry", {"purpose": "Material Issue", "project": ["is", "set"]}))
    print("RECEIPT with_project", c("Stock Entry", {"purpose": "Material Receipt", "project": ["is", "set"]}))
    print("=== 任务/预警 ===")
    print("TASK total", c("Task"), "| proj", c("Task", {"project": ["is", "set"]}))
    print("ALERT total", c("Alert Event"), "| proj", c("Alert Event", {"project": ["is", "set"]}))
    print("ALERTS_BY_RULE:", frappe.db.sql("select rule_code, count(*) c from `tabAlert Event` group by rule_code order by rule_code", as_dict=True))
    print("=== 专业/系统/责任人 覆盖 ===")
    for dt in ["Material Request", "Stock Entry", "Purchase Order"]:
        print(dt, "| disc", c(dt, {"custom_discipline": ["is", "set"]}),
              "| sys", c(dt, {"custom_system": ["is", "set"]}),
              "| resp", c(dt, {"custom_responsible": ["is", "set"]}), "/", c(dt))
    print("=== MR→PO 闭环 ===")
    print("MR_ITEM_ordered>0:", frappe.db.sql("select count(*) c from `tabMaterial Request Item` where ifnull(ordered_qty,0)>0", as_dict=True))
    print("PO_ITEM_with_MR:", frappe.db.sql("select count(*) c from `tabPurchase Order Item` where ifnull(material_request,'')<>''", as_dict=True))
    print("=== 单据间关联样例 ===")
    smp = frappe.db.sql("""select po.name po, po.custom_cb_project proj, po.custom_cb_budget bud,
        ic.name ic, sh.name sh from `tabPurchase Order` po
        left join `tabCB Import Case` ic on ic.purchase_order=po.name
        left join `tabCB Shipment` sh on sh.purchase_order=po.name
        where ifnull(po.custom_cb_project,'')<>'' limit 3""", as_dict=True)
    for s in smp:
        print("CHAIN:", s)
    sys.exit(0)
main()
