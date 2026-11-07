import json
p = "/home/frappe/frappe-bench/apps/cb_erp/cb_erp/cb_erp/doctype/bulk_entry/bulk_entry.json"
d = json.load(open(p, encoding="utf-8"))
for f in d["fields"]:
    if f["fieldname"] in ("discipline", "system", "project", "responsible"):
        print(f["fieldname"], "|", f["fieldtype"], "|", (f.get("options") or "").replace("\n", "/"))
