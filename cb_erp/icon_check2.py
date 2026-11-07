# -*- coding: utf-8 -*-
import re


def run():
    p = "/home/frappe/frappe-bench/apps/frappe/frappe/public/icons/lucide.svg"
    txt = open(p, encoding="utf-8", errors="ignore").read()
    ids = re.findall(r'id="([^"]+)"', txt)
    for kw in ("chart", "pencil", "pie", "check", "edit", "list"):
        hits = [i for i in ids if kw in i][:14]
        print(kw, "->", hits)
    return "OK"
