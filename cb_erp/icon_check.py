# -*- coding: utf-8 -*-
import re


def run():
    p = "/home/frappe/frappe-bench/apps/frappe/frappe/public/icons/lucide.svg"
    txt = open(p, encoding="utf-8", errors="ignore").read()
    ids = re.findall(r'id="([^"]+)"', txt)
    print("IDS_SAMPLE:", ids[:15])
    want = ["layout-dashboard", "zap", "file-text", "shopping-cart", "package", "log-out",
            "clipboard-list", "bar-chart-2", "layers", "edit-3", "pie-chart", "search", "users",
            "truck", "globe", "check-circle", "box", "folder", "award", "bell", "settings"]
    have = {w: (("icon-" + w) in ids or w in ids) for w in want}
    print("HAVE:", have)
    return "OK"
