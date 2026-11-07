# -*- coding: utf-8 -*-
# 三级物料分类：大类(Item Group, is_group=1) -> 中类(is_group=1) -> 小类(is_group=0)
# 并把现有物料按原分类迁入对应小类。
import hashlib
import frappe


def _chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

ROOT = "所有物料组"

# L1: {L2: [L3, ...]}
TAXONOMY = {
    "管道与阀门": {
        "管材": ["钢管", "不锈钢管", "PVC/PE管", "管件"],
        "阀门": ["闸阀", "截止阀", "球阀", "蝶阀", "止回阀", "调节阀"],
        "法兰紧固": ["法兰", "螺栓螺母", "垫片"],
    },
    "电气与电缆": {
        "电缆": ["电力电缆", "控制电缆", "通信电缆", "电线"],
        "配电设备": ["配电柜", "断路器", "接触器", "继电器"],
        "照明": ["灯具", "光源", "开关插座"],
        "桥架穿线": ["桥架", "线管", "接线盒"],
    },
    "仪表与自控": {
        "检测仪表": ["压力仪表", "温度仪表", "流量仪表", "液位仪表"],
        "控制系统": ["PLC", "DCS", "变频器", "传感器"],
        "仪表辅材": ["仪表阀", "导压管", "接线端子"],
    },
    "机电设备与主材": {
        "机械设备": ["泵", "风机", "空调机组", "起重设备"],
        "钢材结构": ["型钢", "钢板", "支吊架"],
        "焊接材料": ["焊条", "焊丝", "焊剂"],
    },
    "五金辅材": {
        "紧固件": ["螺栓", "螺母", "垫圈"],
        "通用五金": ["轴承", "密封件", "手动工具"],
    },
    "防腐保温": {
        "防腐材料": ["涂料", "防腐胶带"],
        "保温材料": ["岩棉", "橡塑", "铝皮"],
    },
    "消防": {
        "消防设备": ["喷淋头", "报警阀", "灭火器"],
        "消防管件": ["消防管", "消防管配件"],
    },
    "其他": {
        "其他物料": ["其他物资"],
    },
}

# 旧分类 -> 新 L1
OLD_MAP = {
    "管道阀门": "管道与阀门",
    "电缆电气": "电气与电缆",
    "仪表自控": "仪表与自控",
    "机电主材": "机电设备与主材",
}
OLD_LEAVES = list(OLD_MAP.keys())


def _ensure_group(name, parent, is_group):
    if parent == name:
        raise ValueError("group cannot be its own parent: %s" % name)
    if frappe.db.exists("Item Group", name):
        d = frappe.get_doc("Item Group", name)
        changed = False
        if int(d.is_group or 0) != is_group:
            d.is_group = is_group
            changed = True
        if parent and d.parent_item_group != parent:
            d.parent_item_group = parent
            changed = True
        if changed:
            d.save(ignore_permissions=True)
        return name
    frappe.get_doc({"doctype": "Item Group", "item_group_name": name,
                    "parent_item_group": parent, "is_group": is_group}).insert(ignore_permissions=True)
    return name


def build_groups():
    for l1, l2map in TAXONOMY.items():
        _ensure_group(l1, ROOT, 1)
        for l2, l3list in l2map.items():
            _ensure_group(l2, l1, 1)
            for l3 in l3list:
                _ensure_group(l3, l2, 0)
    frappe.db.commit()
    return {"L1": frappe.db.count("Item Group", {"parent_item_group": ROOT, "is_group": 1}),
            "L2": sum(len(v) for v in TAXONOMY.values()),
            "L3": sum(len(l3) for v in TAXONOMY.values() for l3 in v.values())}


def _leaves(l1):
    return [l3 for l3list in TAXONOMY[l1].values() for l3 in l3list]


def reclassify():
    items = frappe.get_all("Item", fields=["item_code", "item_group", "item_name"])
    updates = {}
    for it in items:
        target = None
        if it.item_code.startswith("CB-GV"):
            target = "闸阀"
        elif it.item_code.startswith("CB-EL"):
            target = "电力电缆"
        elif it.item_group in OLD_MAP:
            l1 = OLD_MAP[it.item_group]
            lst = _leaves(l1)
            if lst:
                h = int(hashlib.md5(it.item_code.encode("utf-8")).hexdigest(), 16)
                target = lst[h % len(lst)]
        if target:
            updates.setdefault(target, []).append(it.item_code)
    total = 0
    for tg, codes in updates.items():
        for chunk in _chunks(codes, 200):
            ph = ",".join(["%s"] * len(chunk))
            frappe.db.sql("update `tabItem` set item_group=%s where item_code in (%s)" % ("%s", ph), [tg] + chunk)
            total += len(chunk)
    frappe.db.commit()
    frappe.clear_cache()
    return total


def cleanup_old_groups():
    removed = []
    for g in OLD_LEAVES:
        if not frappe.db.exists("Item Group", g):
            continue
        has_items = frappe.db.count("Item", {"item_group": g})
        has_child = frappe.db.count("Item Group", {"parent_item_group": g})
        if has_items == 0 and has_child == 0:
            try:
                frappe.delete_doc("Item Group", g, force=True)
                removed.append(g)
            except Exception as e:
                print("OLD_GROUP_DEL_ERR", g, repr(e)[:120])
    frappe.db.commit()
    return removed


def run():
    counts = build_groups()
    moved = reclassify()
    removed = cleanup_old_groups()
    print("GROUPS", counts, "| ITEMS_MOVED", moved, "| OLD_REMOVED", removed)
    # 校验：每个 L1 下物料数
    for l1 in TAXONOMY:
        n = 0
        for l2 in TAXONOMY[l1]:
            for l3 in TAXONOMY[l1][l2]:
                n += frappe.db.count("Item", {"item_group": l3})
        print("L1_ITEMS", l1, n)
    print("ITEM_GROUP_TOTAL", frappe.db.count("Item Group"))
    print("ITEM_TOTAL", frappe.db.count("Item"))
    return "TAXONOMY_DONE " + str(counts)
