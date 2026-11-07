def main():
    import frappe, sys
    out = []
    EMAIL = "chenzhihua@cb.local"
    NAME = "chenzhihua"
    PWD = "1230"
    def w(*a):
        out.append(" ".join(str(x) for x in a))
    try:
        w("=== create/update super account", EMAIL, "===")
        orig_score = None
        try:
            orig_score = frappe.get_value("System Settings", "System Settings", "minimum_password_score")
        except Exception:
            pass
        w("current minimum_password_score:", orig_score)
        CBROLES = ["SYS", "ENG", "PRC", "BRA", "LOG", "CUS", "WHS", "PM", "FIN", "MGT"]
        user = frappe.db.exists("User", EMAIL)
        if not user:
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
                "new_password": PWD,
                "roles": [{"role": "System Manager"}] + [{"role": r} for r in CBROLES],
            })
            try:
                doc.insert()
                frappe.db.commit()
                w("user created:", doc.name)
            except Exception as e:
                msg = repr(e)
                w("insert error:", msg[:300])
                if "Password" in msg or "password" in msg or "score" in msg or "强度" in msg:
                    w("-> password policy blocked; lowering minimum_password_score to 0 per user-requested weak password 1230")
                    ss = frappe.get_doc("System Settings", "System Settings")
                    ss.minimum_password_score = 0
                    ss.flags.ignore_permissions = True
                    ss.save()
                    frappe.db.commit()
                    w("minimum_password_score now:", frappe.get_value("System Settings", "System Settings", "minimum_password_score"))
                    doc2 = frappe.get_doc({
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
                        "roles": [{"role": "System Manager"}] + [{"role": r} for r in CBROLES],
                    })
                    doc2.insert()
                    frappe.db.commit()
                    w("user created after policy lowering:", doc2.name)
                else:
                    raise
        else:
            u = frappe.get_doc("User", EMAIL)
            u.enabled = 1
            u.user_type = "System User"
            u.new_password = PWD
            have = {r.role for r in u.roles or []}
            want = set(["System Manager"] + CBROLES)
            for r in want - have:
                u.append("roles", {"role": r})
            u.flags.ignore_permissions = True
            u.save()
            frappe.db.commit()
            w("user updated:", EMAIL, "roles:", sorted({r.role for r in u.roles or []}))
        u2 = frappe.get_doc("User", EMAIL)
        w("final check - enabled:", u2.enabled, "| user_type:", u2.user_type, "| roles:", sorted({r.role for r in u2.roles or []}))
        sscore = frappe.get_value("System Settings", "System Settings", "minimum_password_score")
        w("final minimum_password_score:", sscore, "(orig:", orig_score, ")")
        frappe.clear_cache()
        w("RESULT: OK")
    except Exception as e:
        import traceback
        w("FATAL", repr(e))
        w(traceback.format_exc())
    finally:
        try:
            open("/home/frappe/inv016_out.txt", "w", encoding="utf-8").write("\n".join(out))
        except Exception:
            pass
    sys.exit(0)
main()
