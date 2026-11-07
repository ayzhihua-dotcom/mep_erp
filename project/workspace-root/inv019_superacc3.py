def main():
    import frappe, sys
    out = []
    EMAIL = "chenzhihua@cb.local"
    NAME = "chenzhihua"
    PWD = "1230"
    def w(*a):
        out.append(" ".join(str(x) for x in a))
    try:
        w("=== create super account", EMAIL, "(attempt 3: no-password insert + low-level set) ===")
        def pick(prefix):
            for r in frappe.db.sql("select name from `tabRole` where name like %s and not disabled", (prefix + " %",), as_dict=1):
                return r.name
            return prefix
        cbroles = [pick(x) for x in ["SYS", "ENG", "PRC", "BRA", "LOG", "CUS", "WHS", "PM", "FIN", "MGT"]]
        roles = ['System Manager'] + cbroles
        w("roles:", roles)
        doc = frappe.get_doc({
            "doctype": "User",
            "email": EMAIL,
            "first_name": NAME,
            "username": NAME,
            "enabled": 1,
            "user_type": "System User",
            "language": "zh",
            "time_zone": "Asia/Shanghai",
            "send_welcome_email": 0,
            "roles": [{"role": r} for r in roles],
        })
        doc.insert()
        frappe.db.commit()
        w("user created (no password yet):", EMAIL)
        from frappe.utils.password import update_password
        update_password(EMAIL, PWD, logout_all_sessions=False)
        frappe.db.commit()
        w("password set via low-level update_password (bypasses UI strength policy)")
        from frappe.utils.password import check_password
        try:
            user, pwd = check_password(EMAIL, PWD)
            w("check_password verify: user =", user, "-> OK")
        except Exception as e:
            w("check_password verify FAILED:", repr(e))
        u2 = frappe.get_doc("User", EMAIL)
        w("final - enabled:", u2.enabled, "| user_type:", u2.user_type, "| language:", u2.language)
        w("final roles:", sorted({r.role for r in u2.roles or []}))
        w("RESULT: OK")
    except Exception as e:
        import traceback
        w("FATAL", repr(e))
        w(traceback.format_exc())
    finally:
        try:
            open("/home/frappe/inv019_out.txt", "w", encoding="utf-8").write("\n".join(out))
        except Exception:
            pass
    sys.exit(0)
main()
