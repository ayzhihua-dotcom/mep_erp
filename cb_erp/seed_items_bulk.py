# -*- coding: utf-8 -*-
# 按三级分类批量生成物料（演示/压测用），每个叶子类补到 per_leaf 条。
import random
import frappe
from frappe.utils import now_datetime
from cb_erp.cb_erp.item_taxonomy_v2 import TAXONOMY

L1_CODE = {
    "管道与阀门": "PIP", "给排水": "PLB", "消防": "FIR", "暖通空调": "HVAC",
    "电气与电缆": "ELEC", "弱电与通信": "ELV", "仪表与自控": "INST",
    "机电设备与主材": "MECH", "五金辅材": "HW", "防腐保温": "INS",
    "钢结构与建筑": "STL", "焊接与辅材": "WELD", "安全与临时设施": "SAFE", "其他": "MISC",
}
METER_LEAVES = {
    "钢管", "不锈钢管", "PVC/PE管", "衬里管", "合金钢管", "铸铁管", "铜管",
    "给水钢管", "PPR管", "给水PE管", "给水铜管", "排水PVC管", "铸铁排水管",
    "消防管", "电力电缆", "控制电缆", "通信电缆", "电线", "网线", "光缆",
    "型钢", "钢板", "彩钢板", "角钢", "槽钢", "工字钢", "H型钢", "接地扁钢",
    "避雷带", "镀锌风管", "不锈钢风管", "风管保温", "冷媒管", "导压管",
    "仪表穿线管", "接地线", "电伴热带", "防腐胶带", "母线",
}
TAI_LEAVES = {
    "泵", "风机", "空调机组", "起重设备", "风机盘管", "冷水机组", "冷却塔",
    "新风机组", "离心风机", "轴流风机", "屋顶风机", "排烟风机", "换热器",
    "冷却器", "冷凝器", "空压机", "输送机", "电动葫芦", "水处理设备",
    "加药装置", "机柜", "消防水箱", "变压器", "电焊机", "切割机", "角磨机", "电钻",
}


def _uoms():
    u = frappe.get_all("UOM", pluck="name")
    def pick(*c):
        for x in c:
            if x in u:
                return x
        return u[0]
    return (pick("米", "m", "Meter"), pick("台", "Nos", "个"), pick("Nos", "个", "件", "Pcs"))


def _uom_for(leaf, um, ut, uno):
    if leaf in METER_LEAVES:
        return um
    if leaf in TAI_LEAVES:
        return ut
    return uno


def seed_items(per_leaf=48, chunk=400):
    frappe.set_user("Administrator")
    um, ut, uno = _uoms()
    now = now_datetime()
    fields = ["name", "item_code", "item_name", "item_group", "stock_uom", "is_stock_item",
              "valuation_rate", "disabled", "has_batch_no", "has_serial_no",
              "creation", "modified", "owner", "modified_by", "docstatus"]
    if frappe.db.has_column("Item", "custom_qc_required"):
        fields.append("custom_qc_required")
    seq = frappe.db.count("Item")
    values = []
    added = 0
    for l1, l2map in TAXONOMY.items():
        for l2, l3list in l2map.items():
            for l3 in l3list:
                existing = frappe.db.count("Item", {"item_group": l3})
                need = max(0, per_leaf - existing)
                for i in range(need):
                    seq += 1
                    code = "MAT-%06d" % seq
                    name = "%s-%04d" % (l3, existing + i + 1)
                    row = [code, code, name, l3, _uom_for(l3, um, ut, uno), 1,
                           random.randint(10, 5000), 0, 0, 0, now, now, "Administrator", "Administrator", 0]
                    if "custom_qc_required" in fields:
                        row.append(0)
                    values.append(tuple(row))
                    added += 1
                if len(values) >= chunk:
                    frappe.db.bulk_insert("Item", fields, values, ignore_duplicates=True)
                    values = []
    if values:
        frappe.db.bulk_insert("Item", fields, values, ignore_duplicates=True)
    frappe.db.commit()
    frappe.clear_cache()
    print("ADDED_ITEMS", added, "| ITEM_TOTAL", frappe.db.count("Item"))
    # 每个 L1 统计
    for l1, l2map in TAXONOMY.items():
        n = 0
        for l2, l3list in l2map.items():
            for l3 in l3list:
                n += frappe.db.count("Item", {"item_group": l3})
        print("L1_ITEMS", l1, n)
    return "SEED_ITEMS_DONE added=%s total=%s" % (added, frappe.db.count("Item"))
