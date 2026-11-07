# -*- coding: utf-8 -*-
"""把 /desk 与 /desk/home 统一重定向到 MEP 工作台，避免落到空的 /apps 页面。"""
from urllib.parse import quote

MEP_HOME = "/desk/cb-erp/" + quote("巴西机电erp系统测试")


def redirect_desk_home(response=None, request=None):
    """after_request：直接改写响应为 302，避免在 before_request 抛异常导致 500。"""
    try:
        path = getattr(request, "path", "") if request else ""
        method = getattr(request, "method", "GET") if request else "GET"
        if method != "GET" or path not in ("/desk", "/desk/", "/desk/home", "/desk/home/"):
            return
        if response is None:
            return
        response.status_code = 302
        response.headers["Location"] = MEP_HOME
        response.set_data("")
    except Exception:
        return
