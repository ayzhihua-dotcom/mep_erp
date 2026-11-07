import sys, json, os
def main():
    try:
        path = os.path.join(frappe.local.sites_path, frappe.local.site, "site_config.json")
        with open(path) as f:
            cfg = json.load(f)
        before = cfg.get("trusted_hosts")
        vals = ["localhost", "127.0.0.1", "dev.localhost", "*.localhost"]
        existing = cfg.get("trusted_hosts")
        if isinstance(existing, list):
            for v in existing:
                if v not in vals:
                    vals.append(v)
        cfg["trusted_hosts"] = vals
        with open(path, "w") as f:
            json.dump(cfg, f, indent=2, ensure_ascii=False)
        print("PATH:", path)
        print("BEFORE_TRUSTED_HOSTS:", before)
        print("AFTER_TRUSTED_HOSTS:", cfg["trusted_hosts"])
    except Exception as e:
        print("ERR:", repr(e))
    sys.exit(0)
main()
