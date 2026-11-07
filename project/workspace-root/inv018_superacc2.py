def main():
    import frappe, sys
    out = []
    EMAIL = "chenzhihua@cb.local"
    NAME = "chenzhihua"
    PWD = "1230"
    def w(*a):
        out.append(" ".join(str(x) for x in a))
    try:
        w("=== create super account", EMAIL, "(attempt 2) ===")
        orig_score = None
        try:
            orig_score = frappe.get_value("System Settings", "System Settings", "minimum_password_score")
        except Exception:
            pass
        w("minimum_password_score:", orig_score)
        def pick(prefix):
            for r in frappe.db.sql("select name from `tabRole` where name like %s and not disabled", (prefix + " %",), as_dict=1):
                return r.name
            return prefix
        cbroles = [pick(x) for x in ["SYS", "ENG", "PRC", "BRA", "LOG", "CUS", "WHS", "PM", "FIN", "MGT"]]
        w("resolved CB roles:", cbroles)
        roles = ['System Manager'] + cbroles
        def build():
            return frappe.get_doc({
                "doctype": "User",
                "email": EMAIL,
                "first_name": NAME,
                "username": NAME,
                "enabled": 1,
                "user_type": "System User",
                "language": "zh",
                "time_zone": "Asia/Shanghai",
                "send_welcome_email": 0,
                "new_password": PWD,
                "roles": [{"role": r} for r in roles],
            })
        try:
            u = build()
            u.insert()
            frappe.db.commit()
            w("user created:", EMAIL)
            policy_lowered = False
        except Exception as e:
            msg = repr(e)
            w("insert error:", msg[:400])
            if ("password" in msg.lower()) or ("强度" in msg) or ("short" in msg.lower()):
                w("-> password policy blocked 1230; lowering minimum_password_score per user instruction")
                ss = frappe.get_doc("System Settings", "System Settings")
                ss.minimum_password_score = 0
                ss.flags.ignore_permissions = True
                ss.save()
                frappe.db.commit()
                policy_lowered = True
                u = build()
                u.insert()
                frappe.db.commit()
                w("user created after policy lowering:", EMAIL)
            else:
                raise
        u2 = frappe.get_doc("User", EMAIL)
        final_roles = sorted({r.role for r in u2.roles or []})
        w("final - enabled:", u2.enabled, "| user_type:", u2.user_type, "| roles:", final_roles)
        w("final minimum_password_score:", frappe.get_value("System Settings", "System Settings", "minimum_password_score"))
        frappe.clear_cache()
        w("RESULT: OK")
    except Exception as e:
        import traceback
        w("FATAL", repr(e))
        w(traceback.format_exc())
    finally:
        try:
            open("/home/frappe/inv018_out.txt", "w", encoding="utf-8").write("\n".join(out))
        except Exception:
            pass
    sys.exit(0)
main()
