# -*- coding: utf-8 -*-
# 全站简体中文收口：语言设置 + 翻译词条（zh）
import frappe

PAIRS = {
    # 品牌与模块显示名
    "CB ERP": "工作台",
    "Cb Erp": "工作台",
    # CB 自定义 DocType
    "Design BOM": "设计BOM",
    "Design BOM Item": "设计BOM明细",
    "Design Change Request": "设计变更申请",
    "Material Budget": "材料预算",
    "Material Budget Detail": "材料预算明细",
    "Material Commitment": "材料承诺",
    "CB Shipment": "装运管理",
    "CB Shipment Line": "装运明细",
    "CB Shipment Milestone": "装运里程碑",
    "CB Import Case": "进口案件",
    "CB Import Checklist": "进口单证清单",
    "CB Import Cost": "进口费用",
    "CB Import Allocation": "进口费用分摊",
    "CB Allocation Cost": "分摊费用行",
    "CB Allocation Item": "分摊明细",
    "CB Cost Audit Log": "成本审计日志",
    "Alert Rule": "预警规则",
    "Alert Event": "预警事件",
    "Bulk Entry": "批量录入",
    # 标准 DocType
    "Item": "物料",
    "Item Group": "物料分类",
    "Warehouse": "仓库",
    "Project": "项目",
    "Supplier": "供应商",
    "Customer": "客户",
    "Company": "公司",
    "User": "用户",
    "Role": "角色",
    "Task": "任务",
    "Stock Entry": "库存移动",
    "Material Request": "采购申请",
    "Purchase Order": "采购订单",
    "Request for Quotation": "询价单",
    "Supplier Quotation": "供应商报价",
    "Quality Inspection": "质检单",
    "Stock Reconciliation": "库存盘点",
    "Material Receipt": "其他入库",
    "Material Issue": "领料出库",
    "Material Transfer": "直接调拨",
    # 状态
    "Draft": "草稿",
    "Submitted": "已提交",
    "Cancelled": "已取消",
    "Not Saved": "尚未保存",
    "Working": "进行中",
    "Completed": "已完成",
    "Closed": "已关闭",
    "Overdue": "已逾期",
    "Pending Review": "待评审",
    "Template": "模板",
    "On Hold": "暂停",
    "To Bill": "待开票",
    "To Receive": "待收货",
    "To Receive and Bill": "待收货开票",
    # 按钮/界面
    "Save": "保存",
    "Submit": "提交",
    "Cancel": "取消",
    "Delete": "删除",
    "Actions": "操作",
    "Last Edited By": "最后编辑",
    "Created By": "创建人",
    "Modified By": "修改人",
    "Search": "搜索",
    "Notifications": "通知",
    "Settings": "设置",
}


def run():
    frappe.set_user("Administrator")
    frappe.db.set_single_value("System Settings", "language", "zh")
    for u in frappe.get_all("User", filters={"enabled": 1}, pluck="name"):
        if u in ("Administrator", "Guest"):
            continue
        frappe.db.set_value("User", u, "language", "zh", update_modified=False)
    frappe.db.commit()

    for src, tr in PAIRS.items():
        nm = frappe.db.get_value("Translation", {"language": "zh", "source_text": src}, "name")
        if nm:
            frappe.db.set_value("Translation", nm, "translated_text", tr, update_modified=False)
        else:
            try:
                frappe.get_doc({"doctype": "Translation", "language": "zh",
                                "source_text": src, "translated_text": tr}).insert(ignore_permissions=True)
            except Exception as e:
                print("TR_ERR", src, repr(e)[:100])
    frappe.db.commit()
    frappe.clear_cache()
    print("ZH_TRANSLATIONS", frappe.db.count("Translation", {"language": "zh"}))
    # 验证
    frappe.set_user("chenzhihua@cb.local")
    for k in ["Design BOM", "Material Budget", "Bulk Entry", "Stock Entry", "Draft", "Last Edited By"]:
        print("CHECK", k, "->", frappe._(k))
    return "I18N_DONE"
