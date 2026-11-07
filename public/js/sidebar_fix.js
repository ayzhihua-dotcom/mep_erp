// 侧栏兼容修复：Frappe v15 会给 URL 型侧栏项也套上当前模块前缀，
// 导致跨模块链接（如 Stock 侧栏 → /desk/cb-erp/bulk-entry）变成
// /desk/stock/cb-erp/... 而 404。这里只修正「URL 项且已写绝对 /desk/ 路径」的情况。
(function () {
	function patch() {
		try {
			var si = frappe.ui && frappe.ui.sidebar_item;
			if (!si || !si.get_route || si.__cbPatched) return !!si;
			var orig = si.get_route;
			si.get_route = function (item, edit_mode, shell) {
				var path = orig.apply(this, arguments);
				try {
					if (item && item.link_type === "URL" && item.url && item.url.indexOf("/desk/") === 0) {
						var slug = shell && frappe.router && frappe.router.shell_slug ? frappe.router.shell_slug(shell) : "";
						if (slug && path && path.indexOf("/desk/" + slug + "/") === 0) {
							return item.url;
						}
					}
				} catch (e) {}
				return path;
			};
			si.__cbPatched = true;
			return true;
		} catch (e) {
			return false;
		}
	}

	// 侧栏模板对 URL 型条目固定写 target="_blank"，统一改为当前窗口打开（站内链接）。
	function sameTab() {
		try {
			document.querySelectorAll('.body-sidebar a[target="_blank"]').forEach(function (a) {
				var href = a.getAttribute("href") || "";
				if (href.charAt(0) === "/") a.removeAttribute("target");
			});
		} catch (e) {}
	}

	// 统一品牌：侧栏 Logo 加版本号强制刷新，alt 改为 MEP
	function brandLogo() {
		try {
			document.querySelectorAll(".sidebar-header img").forEach(function (img) {
				var src = img.getAttribute("src") || "";
				if (src.indexOf("cb-erp-logo.svg") >= 0 && src.indexOf("?") < 0) {
					img.setAttribute("src", src + "?v=2");
				}
				if (img.alt && img.alt.indexOf("巴西机电") >= 0) img.alt = "MEP 工作台";
			});
		} catch (e) {}
	}

	// 单一入口：禁用侧栏头部的工作区切换菜单（改用「高级功能」页）
	function lockHeader() {
		try {
			document.querySelectorAll(".sidebar-header").forEach(function (h) {
				if (h.__cbLocked) return;
				h.__cbLocked = 1;
				h.addEventListener("click", function (e) {
					e.preventDefault();
					e.stopPropagation();
				}, true);
			});
		} catch (e) {}
	}

	if (!patch()) {
		var n = 0;
		var t = setInterval(function () {
			if (patch() || ++n > 40) clearInterval(t);
		}, 250);
	}

	// 每次路由/侧栏重建后都去掉站内链接的 target=_blank
	sameTab();
	brandLogo();
	lockHeader();
	$(document).on("page-change", function () {
		sameTab();
		brandLogo();
		lockHeader();
	});
	setInterval(function () {
		sameTab();
		brandLogo();
		lockHeader();
	}, 1500);
	try {
		new MutationObserver(function () {
			sameTab();
			brandLogo();
			lockHeader();
		}).observe(document.body, { childList: true, subtree: true });
	} catch (e) {}
})();
