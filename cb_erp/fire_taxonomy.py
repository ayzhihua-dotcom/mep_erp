# -*- coding: utf-8 -*-
"""消防专业细分：消防水 / 消防电。

1) 把旧的 5 个「消防xx」中类拆成 消防水 / 消防电 两个中类、30 个叶子类；
2) 旧叶子类里的物料按语义迁移到新叶子类，再删除旧分类；
3) 按专业实际清单生成消防物料（名称 + 对应规格 + 单位）。
"""
import frappe

ROOT = "所有物料组"
L1 = "消防"
L2_WATER = "消防水"
L2_ELEC = "消防电"

# 旧中类（拆分后删除）
OLD_L2 = ["消防设备", "消防管件", "消防水系统", "消防报警", "灭火系统"]

# 旧叶子 -> 新叶子
OLD_LEAF_MAP = {
    "喷淋头": "自动喷水灭火",
    "报警阀": "自动喷水灭火",
    "灭火器": "灭火器材",
    "消防管": "消防管道",
    "消防管配件": "消防管道配件",
    "消火栓": "消火栓系统",
    "水流指示器": "消防水流监测",
    "消防水箱": "消防水箱水池",
    "消防水池配件": "消防水箱水池",
    "火灾探测器": "火灾探测报警",
    "报警控制器": "火灾报警控制器",
    "声光报警器": "声光警报器",
    "手动报警按钮": "手动报警按钮",
    "气体灭火": "气体灭火系统",
    "泡沫灭火": "泡沫灭火系统",
    "消防炮": "消防炮系统",
}

WATER_LEAVES = [
    "消防泵组", "消防水箱水池", "消火栓系统", "消防水带水枪",
    "自动喷水灭火", "水喷雾雨淋系统", "气体灭火系统", "泡沫灭火系统",
    "消防炮系统", "灭火器材", "消防管道", "消防管道配件",
    "消防阀门", "水泵接合器", "消防水流监测",
]
ELEC_LEAVES = [
    "火灾报警控制器", "火灾探测报警", "手动报警按钮", "声光警报器",
    "消防广播系统", "消防电话系统", "消防联动模块", "消防应急照明",
    "疏散指示标志", "防火门监控系统", "防火卷帘控制", "可燃气体探测",
    "消防电源监控", "消防电缆", "消防桥架线管",
]

# 物料模板：每个「名称」只配它真实存在的规格，避免出现「喷头 DN100」这类错误搭配
FIRE_ITEMS = {
    # ---------------- 消防水 ----------------
    "消防泵组": {"uom": "台", "variants": {
        "消防泵": ["Q=20L/s H=80m 37kW", "Q=30L/s H=100m 55kW", "Q=40L/s H=120m 75kW", "Q=15L/s H=60m 22kW"],
        "稳压泵": ["Q=5L/s H=50m 7.5kW", "Q=10L/s H=60m 11kW", "Q=3L/s H=40m 5.5kW"],
        "柴油机消防泵": ["Q=30L/s H=100m", "Q=50L/s H=140m", "Q=40L/s H=120m"],
        "消防气压罐": ["300L PN16", "500L PN16", "1000L PN16"],
        "消防泵控制柜": ["37kW 星三角", "75kW 软启动", "22kW 直接启动"],
    }},
    "消防水箱水池": {"uom": "台", "variants": {
        "不锈钢消防水箱": ["18m³ 304不锈钢", "36m³ 304不锈钢", "50m³ 304不锈钢", "100m³ 304不锈钢"],
        "装配式消防水箱": ["50m³ 组合式", "100m³ 组合式", "200m³ 组合式"],
        "消防水池液位计": ["量程0~5m 4~20mA", "量程0~3m 投入式", "超声波 0~10m"],
        "水箱自洁消毒器": ["WTS-2A 处理量20m³/h", "WTS-2B 处理量50m³/h"],
        "水箱液位控制阀": ["DN100 遥控浮球", "DN150 遥控浮球"],
    }},
    "消火栓系统": {"uom": "套", "variants": {
        "室内消火栓": ["DN65 单栓", "DN65 双栓", "DN65 减压稳压", "DN65 旋转型"],
        "室外消火栓": ["DN100/65 地上式", "DN100/65 地下式", "DN150/80 地上式"],
        "减压稳压消火栓": ["DN65 进口压力0.4~1.0MPa", "DN65 出口0.35MPa"],
        "旋转型消火栓": ["DN65 90°旋转", "DN65 180°旋转"],
        "消火栓箱": ["800×650×240 钢制", "1000×700×240 不锈钢", "暗装 800×650×240"],
    }},
    "消防水带水枪": {"uom": "套", "variants": {
        "消防水带": ["DN65×25m", "DN50×20m", "DN65×20m 衬胶"],
        "直流水枪": ["φ19", "φ16", "φ22"],
        "开花水枪": ["φ19 开花/直流两用", "φ16 开花"],
        "消防接口": ["KD65 内扣式", "KY65 压式", "KD50 内扣式"],
        "消防软管卷盘": ["JPS1.6-19/30", "JPS0.8-19/25"],
    }},
    "自动喷水灭火": {"uom": "个", "variants": {
        "闭式喷头": ["DN15 68℃ 下垂型", "DN15 68℃ 直立型", "DN20 93℃ 边墙型", "DN15 79℃ 下垂型"],
        "开式喷头": ["DN15 下垂型", "DN20 直立型", "DN15 水幕型"],
        "湿式报警阀": ["DN100 PN16", "DN150 PN16", "DN200 PN16"],
        "干式报警阀": ["DN100 PN16", "DN150 PN16"],
        "预作用报警阀": ["DN100 PN16", "DN150 PN16"],
        "水流指示器": ["DN100 马鞍式", "DN150 马鞍式", "DN80 法兰式"],
        "压力开关": ["DN100 0.6MPa", "DN150 1.6MPa"],
        "末端试水装置": ["DN25 0.6MPa", "DN25 带压力表"],
        "信号阀": ["DN100 PN16", "DN150 PN16"],
    }},
    "水喷雾雨淋系统": {"uom": "套", "variants": {
        "雨淋报警阀组": ["DN100 PN16", "DN150 PN16", "DN200 PN16"],
        "水幕喷头": ["水幕5mm 下垂型", "水幕8mm 侧喷型"],
        "水雾喷头": ["ZSTWB-40/120", "ZSTWB-63/120"],
        "雨淋阀": ["ZSFM-100", "ZSFM-150", "ZSFM-200"],
        "雨淋阀控制盘": ["DN100 电启动", "DN150 电启动"],
    }},
    "气体灭火系统": {"uom": "套", "variants": {
        "七氟丙烷灭火装置": ["40L 柜式", "70L 柜式", "90L 管网式", "120L 管网式"],
        "IG541灭火装置": ["80L 管网式", "90L 管网式"],
        "二氧化碳灭火装置": ["70L 管网式", "40L 柜式"],
        "柜式气体灭火装置": ["单柜 40L", "双柜 2×70L"],
        "气体灭火喷嘴": ["DN20 全淹没", "DN25 全淹没", "DN32 局部应用"],
        "灭火剂钢瓶": ["40L 15MPa", "70L 15MPa", "90L 15MPa"],
        "选择阀": ["DN50 4.2MPa", "DN65 4.2MPa", "DN80 4.2MPa"],
    }},
    "泡沫灭火系统": {"uom": "套", "variants": {
        "泡沫比例混合器": ["PHY-32", "PHY-48", "PHYM-64"],
        "泡沫产生器": ["PCL-8", "PCL-16", "PCL-24"],
        "泡沫液": ["3% AFFF 200L", "6% AFFF 200L", "3% 抗溶 200L"],
        "泡沫喷头": ["DN15 吸气式", "DN20 吸气式"],
        "泡沫消火栓": ["DN65 单阀", "DN100 双阀"],
    }},
    "消防炮系统": {"uom": "台", "variants": {
        "消防水炮": ["PL24 20L/s", "PL32 30L/s", "PS30 30L/s"],
        "自动跟踪定位射流灭火装置": ["ZDMS0.6/5S", "ZDMS0.8/10S"],
        "消防炮塔": ["6m 固定式", "9m 固定式"],
        "炮座": ["DN100 回转式", "DN150 回转式"],
        "移动式消防炮": ["PS20 20L/s", "PL16 16L/s"],
    }},
    "灭火器材": {"uom": "具", "variants": {
        "干粉灭火器": ["MFZ/ABC4", "MFZ/ABC8", "MFZ/ABC1", "MFTZ/ABC35 推车式"],
        "二氧化碳灭火器": ["MT5", "MT7", "MT3"],
        "水基型灭火器": ["MSWZ/3", "MSWZ/6", "MSWJ/9"],
        "推车式灭火器": ["MFTZ/ABC35", "MFTZ/ABC50"],
        "灭火器箱": ["4kg×2 落地式", "8kg×2 落地式", "4kg×4 壁挂式"],
    }},
    "消防管道": {"uom": "米", "variants": {
        "消防专用钢管": ["DN50 内外热镀锌", "DN65 内外热镀锌", "DN100 内外热镀锌"],
        "内外热镀锌钢管": ["DN80", "DN150", "DN200", "DN250"],
        "沟槽式消防管": ["DN100 1.6MPa", "DN150 1.6MPa", "DN200 1.6MPa"],
        "消防用不锈钢管": ["DN65 304", "DN100 304", "DN150 304"],
    }},
    "消防管道配件": {"uom": "个", "variants": {
        "沟槽弯头": ["DN65 90°", "DN100 90°", "DN150 90°", "DN200 90°"],
        "沟槽三通": ["DN100×65", "DN150×100", "DN200×150"],
        "沟槽异径管": ["DN100×65", "DN150×100", "DN200×150"],
        "沟槽卡箍": ["DN65", "DN100", "DN150", "DN200"],
        "机械三通": ["DN100×50", "DN150×65", "DN200×80"],
    }},
    "消防阀门": {"uom": "个", "variants": {
        "消防信号闸阀": ["DN100 PN16", "DN150 PN16", "DN200 PN16"],
        "消防蝶阀": ["DN100 PN16 对夹式", "DN150 PN16 对夹式", "DN200 PN16 法兰式"],
        "消防止回阀": ["DN100 PN16", "DN150 PN16"],
        "消防减压阀": ["DN100 可调式", "DN150 可调式"],
        "消防泄压阀": ["DN80 1.6MPa", "DN100 1.6MPa"],
        "消防闸阀": ["DN65 PN16", "DN80 PN16"],
    }},
    "水泵接合器": {"uom": "套", "variants": {
        "地上式水泵接合器": ["DN100", "DN150", "DN100 双阀"],
        "地下式水泵接合器": ["DN100", "DN150"],
        "墙壁式水泵接合器": ["DN100", "DN150"],
        "多用式水泵接合器": ["DN100 双阀", "DN150 双阀"],
    }},
    "消防水流监测": {"uom": "个", "variants": {
        "水流指示器": ["DN80 马鞍式", "DN100 马鞍式", "DN150 法兰式"],
        "压力开关": ["0.6MPa", "1.6MPa"],
        "流量开关": ["DN100 插入式", "DN150 插入式"],
        "末端试水阀": ["DN25 铜质", "DN20 铜质"],
        "压力传感器": ["0~1.6MPa 4~20mA", "0~2.5MPa 4~20mA"],
    }},
    # ---------------- 消防电 ----------------
    "火灾报警控制器": {"uom": "台", "variants": {
        "火灾报警控制器": ["壁挂 2回路 252点", "壁挂 4回路 504点", "柜式 8回路 1008点"],
        "区域火灾报警控制器": ["壁挂 1回路 126点", "壁挂 2回路 252点"],
        "消防联动控制器": ["柜式 8回路", "柜式 16回路"],
        "火灾显示盘": ["楼层显示 总线制", "区域显示 总线制"],
        "消防控制室图形显示装置": ["19寸 总线制", "27寸 总线制"],
    }},
    "火灾探测报警": {"uom": "个", "variants": {
        "点型光电感烟探测器": ["2线制 编码型", "非编码型", "防爆型"],
        "点型感温探测器": ["A1R 编码型", "B型 定温", "差定温 编码型"],
        "线型光束感烟探测器": ["反射式 5~100m", "反射式 10~40m"],
        "缆式线型感温探测器": ["85℃ 可恢复", "105℃ 不可恢复"],
        "吸气式感烟探测器": ["单管 2000m²", "四管 8000m²"],
        "紫外火焰探测器": ["UV 探测距离25m", "UV/IR 复合型"],
    }},
    "手动报警按钮": {"uom": "个", "variants": {
        "手动火灾报警按钮": ["编码型", "可复位", "带保护罩", "J-SAP-JBF-301"],
        "消火栓按钮": ["编码型 带指示", "非编码型"],
        "带电话插孔手报": ["编码型 带插孔", "IP65 带插孔"],
        "防爆手动报警按钮": ["Exd II CT6", "IP67"],
    }},
    "声光警报器": {"uom": "个", "variants": {
        "声光报警器": ["DC24V 编码型", "DC24V 非编码型", "IP65 编码型"],
        "火灾警铃": ["6寸 DC24V", "8寸 DC24V"],
        "频闪灯": ["15cd", "30cd"],
        "防爆声光报警器": ["Exd II CT6 24V", "IP67 24V"],
    }},
    "消防广播系统": {"uom": "套", "variants": {
        "消防广播功放": ["120W", "240W", "360W", "500W"],
        "消防广播音箱": ["3W 吸顶", "5W 壁挂", "10W 号角"],
        "消防广播分配盘": ["8路", "16路"],
        "广播模块": ["编码型 单路", "编码型 双路"],
        "消防广播中继器": ["8路", "16路"],
    }},
    "消防电话系统": {"uom": "套", "variants": {
        "消防电话主机": ["20门 总线制", "40门 总线制", "60门 总线制"],
        "消防电话分机": ["总线制 壁挂", "多线制 壁挂"],
        "消防电话插孔": ["总线制", "带标识灯"],
        "手提式消防电话": ["总线制 手提", "多线制 手提"],
        "消防电话中继器": ["8门", "16门"],
    }},
    "消防联动模块": {"uom": "个", "variants": {
        "输入模块": ["编码型", "2线制", "GST-LD-8300"],
        "输出模块": ["编码型 继电器输出", "2线制"],
        "输入输出模块": ["编码型", "GST-LD-8301"],
        "总线隔离模块": ["编码型 32点", "编码型 64点"],
        "中继模块": ["编码型 总线中继", "编码型 电源中继"],
    }},
    "消防应急照明": {"uom": "套", "variants": {
        "消防应急照明灯": ["3W 双头 90min", "5W 双头 90min", "8W 双头 120min"],
        "应急照明集中电源": ["A型 0.5kVA", "A型 1kVA", "A型 2kVA"],
        "应急照明配电箱": ["集中电源型 1kVA", "集中电源型 2kVA"],
        "防爆应急照明灯": ["Exd II CT6 3W", "IP65 5W"],
    }},
    "疏散指示标志": {"uom": "套", "variants": {
        "安全出口标志灯": ["集中电源型 350×150", "自带电源型 350×150", "双面 350×150"],
        "疏散指示标志灯": ["集中电源型 350×150", "自带电源型 350×150", "地埋式"],
        "蓄光型疏散标志": ["350×150", "300×100"],
        "地面疏散指示标志": ["300×100 地埋式", "400×150 地埋式"],
    }},
    "防火门监控系统": {"uom": "套", "variants": {
        "防火门监控主机": ["2回路 128点", "4回路 256点"],
        "防火门监控模块": ["常闭门 单门", "常开门 双门"],
        "门磁开关": ["明装", "暗装"],
        "电磁释放器": ["常开门 65kg", "常开门 120kg"],
        "闭门器": ["65kg", "85kg", "120kg"],
    }},
    "防火卷帘控制": {"uom": "套", "variants": {
        "防火卷帘控制器": ["单帘 带备用电源", "双帘 带备用电源"],
        "卷帘手动控制按钮": ["单帘", "双帘"],
        "卷帘限位器": ["上限位 机械式", "下限位 机械式"],
        "卷帘温控释放装置": ["72℃", "带烟感联动"],
    }},
    "可燃气体探测": {"uom": "个", "variants": {
        "可燃气体探测器": ["甲烷 4~20mA", "液化石油气 4~20mA", "氢气 催化燃烧"],
        "可燃气体报警控制器": ["4路", "8路", "16路"],
        "燃气紧急切断阀": ["DN50 常开", "DN80 常开", "DN100 常开"],
        "点型红外可燃气体探测器": ["0~100%LEL", "0~100%LEL 防爆"],
    }},
    "消防电源监控": {"uom": "套", "variants": {
        "消防设备电源监控主机": ["32点", "64点", "128点"],
        "电压传感器": ["AC220V", "AC380V"],
        "电流传感器": ["0~100A", "0~400A"],
        "双电源切换箱": ["63A PC级", "100A PC级", "160A CB级"],
    }},
    "消防电缆": {"uom": "米", "variants": {
        "耐火电力电缆": ["NH-YJV 4×16", "NH-YJV 5×16", "NH-YJV 4×35"],
        "阻燃电力电缆": ["ZR-YJV 4×25", "ZR-YJV 4×50"],
        "消防控制电缆": ["WDZBN-KYJY 4×1.5", "NH-KVV 7×1.5", "WDZBN-KYJY 8×1.5"],
        "矿物绝缘电缆": ["BTTZ 4×10", "BTTZ 3×25", "BTTZ 4×25"],
    }},
    "消防桥架线管": {"uom": "米", "variants": {
        "防火桥架": ["200×100", "300×100", "400×150"],
        "消防镀锌线管": ["JDG20", "JDG25", "SC25", "SC32"],
        "防火封堵材料": ["阻火包 240×120×60", "防火泥 20kg/箱"],
        "接线盒": ["86型 金属", "86型 防火", "防爆型"],
    }},
}


def _ensure_group(name, parent, is_group):
    if frappe.db.exists("Item Group", name):
        doc = frappe.get_doc("Item Group", name)
        if doc.parent_item_group != parent:
            if frappe.db.count("Item Group", {"parent_item_group": name}):
                frappe.throw("Item Group %s 已是有子类的分组，不能改作叶子类" % name)
            doc.parent_item_group = parent
            doc.is_group = is_group
            doc.save(ignore_permissions=True)
        return name
    frappe.get_doc({"doctype": "Item Group", "item_group_name": name,
                    "parent_item_group": parent, "is_group": is_group}).insert(ignore_permissions=True)
    return name


def install_groups():
    frappe.set_user("Administrator")
    _ensure_group(L1, ROOT, 1)
    _ensure_group(L2_WATER, L1, 1)
    _ensure_group(L2_ELEC, L1, 1)
    for leaf in WATER_LEAVES:
        _ensure_group(leaf, L2_WATER, 0)
    for leaf in ELEC_LEAVES:
        _ensure_group(leaf, L2_ELEC, 0)

    # 旧物料迁移
    moved = 0
    for old_leaf, new_leaf in OLD_LEAF_MAP.items():
        if not frappe.db.exists("Item Group", old_leaf):
            continue
        n = frappe.db.count("Item", {"item_group": old_leaf})
        if n and old_leaf != new_leaf:
            frappe.db.sql("update `tabItem` set item_group=%s where item_group=%s", (new_leaf, old_leaf))
            moved += n

    # 删除旧叶子与旧中类（先叶子后中类）
    new_leaves = set(WATER_LEAVES) | set(ELEC_LEAVES)
    for old_leaf in OLD_LEAF_MAP:
        if old_leaf in new_leaves or not frappe.db.exists("Item Group", old_leaf):
            continue
        if frappe.db.count("Item", {"item_group": old_leaf}):
            continue
        if frappe.db.count("Item Group", {"parent_item_group": old_leaf}):
            continue
        frappe.delete_doc("Item Group", old_leaf, force=1, ignore_permissions=True)
    for old_l2 in OLD_L2:
        if not frappe.db.exists("Item Group", old_l2):
            continue
        if frappe.db.count("Item Group", {"parent_item_group": old_l2}):
            continue
        if frappe.db.count("Item", {"item_group": old_l2}):
            continue
        frappe.delete_doc("Item Group", old_l2, force=1, ignore_permissions=True)

    frappe.db.commit()
    frappe.clear_cache()
    print("MOVED_ITEMS:", moved)
    print("L2_UNDER_FIRE:", frappe.get_all("Item Group", filters={"parent_item_group": L1}, pluck="name"))
    for l2 in (L2_WATER, L2_ELEC):
        print(l2, "LEAVES:", frappe.db.count("Item Group", {"parent_item_group": l2}))
    return "INSTALL_DONE"


def _fire_groups():
    groups = []
    for l2 in (L2_WATER, L2_ELEC):
        groups += frappe.get_all("Item Group", filters={"parent_item_group": l2}, pluck="name")
    return groups


def _next_seq():
    rows = frappe.db.sql("""select item_code from `tabItem` where item_code like 'MAT-%%'""", as_dict=True)
    seq = 0
    for r in rows:
        try:
            seq = max(seq, int(r["item_code"].split("-")[1]))
        except Exception:
            pass
    return max(seq, frappe.db.count("Item"))


def seed_items(per_leaf=24):
    frappe.set_user("Administrator")
    from frappe.utils import now_datetime
    seq = _next_seq()
    now = now_datetime()
    fields = ["name", "item_code", "item_name", "item_group", "stock_uom", "is_stock_item",
              "valuation_rate", "disabled", "has_batch_no", "has_serial_no",
              "creation", "modified", "owner", "modified_by", "docstatus"]
    if frappe.db.has_column("Item", "custom_spec"):
        fields.append("custom_spec")
    if frappe.db.has_column("Item", "custom_qc_required"):
        fields.append("custom_qc_required")

    values, added = [], 0
    for leaf, cfg in FIRE_ITEMS.items():
        if not frappe.db.exists("Item Group", leaf):
            print("SKIP_MISSING_GROUP", leaf)
            continue
        have = frappe.db.count("Item", {"item_group": leaf})
        need = max(0, per_leaf - have)
        combos = []
        for nm, specs in cfg["variants"].items():
            for sp in specs:
                combos.append((nm, sp))
        need = min(need, len(combos))
        for i in range(need):
            nm, sp = combos[i]
            seq += 1
            code = "MAT-%06d" % seq
            row = [code, code, nm, leaf, cfg["uom"], 1, 0, 0, 0, 0,
                   now, now, "Administrator", "Administrator", 0]
            if "custom_spec" in fields:
                row.append(sp)
            if "custom_qc_required" in fields:
                row.append(0)
            values.append(tuple(row))
            added += 1
        if len(values) >= 300:
            frappe.db.bulk_insert("Item", fields, values, ignore_duplicates=True)
            values = []
    if values:
        frappe.db.bulk_insert("Item", fields, values, ignore_duplicates=True)
    frappe.db.commit()
    frappe.clear_cache()
    print("ADDED:", added, "| TOTAL_ITEMS:", frappe.db.count("Item"))
    return added


def reset_items():
    """删除消防叶子类下的物料（用于替换成真实清单，已确认无单据引用）。"""
    frappe.set_user("Administrator")
    groups = _fire_groups()
    codes = frappe.get_all("Item", filters={"item_group": ["in", groups]}, pluck="name")
    n = 0
    for code in codes:
        try:
            frappe.delete_doc("Item", code, force=1, ignore_permissions=True, delete_permanently=True)
            n += 1
        except Exception as e:
            print("DEL_FAIL", code, repr(e)[:120])
    frappe.db.commit()
    frappe.clear_cache()
    print("DELETED:", n, "of", len(codes))
    return n


def stats():
    for l2 in (L2_WATER, L2_ELEC):
        leaves = frappe.get_all("Item Group", filters={"parent_item_group": l2}, pluck="name", order_by="name")
        total = 0
        for lf in leaves:
            n = frappe.db.count("Item", {"item_group": lf})
            total += n
            print("   ", lf, n)
        print(l2, "LEAVES:", len(leaves), "ITEMS:", total)
    bad = frappe.db.sql("""select count(*) c from `tabItem` i
                           join `tabItem Group` g on g.name=i.item_group where g.is_group=1""", as_dict=True)
    print("ITEMS_ON_GROUP_NODES:", bad[0]["c"])


def run(per_leaf=24):
    install_groups()
    seed_items(per_leaf=int(per_leaf))
    stats()
    return "FIRE_DONE"


def reset_run():
    install_groups()
    reset_items()
    seed_items(per_leaf=24)
    stats()
    return "FIRE_RESET_DONE"
