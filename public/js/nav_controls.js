// 全局返回 / 前进：应用内路由栈（不依赖浏览器 history），页头显式按钮 + Alt+←/→
(function () {
	var stack = [];
	var idx = -1;
	var suppress = false;

	function route() {
		try {
			return (frappe.get_route && frappe.get_route()) || [];
		} catch (e) {
			return [];
		}
	}

	function key(r) {
		return JSON.stringify(r || []);
	}

	function push(r) {
		if (suppress) return;
		if (idx >= 0 && key(stack[idx]) === key(r)) return;
		stack = stack.slice(0, idx + 1);
		stack.push(r);
		idx = stack.length - 1;
		if (stack.length > 80) {
			stack.shift();
			idx--;
		}
		update();
	}

	function go(dir) {
		var ni = idx + dir;
		if (ni < 0 || ni >= stack.length) return;
		idx = ni;
		suppress = true;
		try {
			var target = stack[ni];
			if (target && target[0] === "Workspaces") {
				if (target[1] === "巴西机电ERP系统测试") {
					frappe.set_route("cb-erp", "巴西机电erp系统测试");
				} else {
					frappe.set_route(frappe.router.slug(target[1]));
				}
			} else {
				frappe.set_route(target);
			}
		} catch (e) {
			suppress = false;
		}
		setTimeout(function () {
			suppress = false;
			update();
		}, 700);
		update();
	}

	function update() {
		var b = document.getElementById("cb-nav-back");
		var f = document.getElementById("cb-nav-forward");
		if (b) b.disabled = idx <= 0;
		if (f) f.disabled = idx >= stack.length - 1;
	}

	// A+ 专注模式：深页（非 MEP 模块）默认收起标准侧栏
	function currentShell() {
		try {
			var m = (frappe.app && frappe.app.sidebar && frappe.app.sidebar.current_module) || "";
			var r = route();
			if ((r[0] === "List" || r[0] === "Form" || r[0] === "Tree") && r[1]) {
				try {
					var mod = frappe.get_meta(r[1]).module;
					if (mod) m = mod;
				} catch (e) {}
			}
			return m || "";
		} catch (e) {
			return "";
		}
	}

	var lastPath = "";
	function applyFocus() {
		try {
			if (location.pathname !== lastPath) {
				lastPath = location.pathname;
				window.__cbShowMenu = false;
			}
		} catch (e) {}
		var m = currentShell();
		var on = !!m && m !== "CB ERP" && m !== "Private" && !window.__cbShowMenu;
		document.body.classList.toggle("cb-focus-mode", on);
		try {
			if (!on && m === "CB ERP" && document.body.classList.contains("sidebar-collapsed") &&
				frappe.app && frappe.app.sidebar && frappe.app.sidebar.open) {
				frappe.app.sidebar.open();
			}
		} catch (e) {}
		var btn = document.getElementById("cb-adv-menu");
		if (btn && document.body.classList.contains("cb-focus-mode") === false && m !== "CB ERP") {
			btn.textContent = "隐藏菜单";
		} else if (btn) {
			btn.textContent = "菜单";
		}
	}

	function visibleHead() {
		var heads = Array.from(document.querySelectorAll(".page-head")).filter(function (e) {
			return e.offsetParent !== null;
		});
		return heads.length ? heads[heads.length - 1] : null;
	}

	function build() {
		var head = visibleHead();
		if (!head) return;
		var title = head.querySelector(".page-title") || head;
		var wrap = document.getElementById("cb-nav-inline");
		if (!wrap) {
			wrap = document.createElement("div");
			wrap.id = "cb-nav-inline";
			wrap.innerHTML =
				'<button type="button" id="cb-nav-home" title="返回 MEP 工作台">⌂ MEP</button>' +
				'<button type="button" id="cb-adv-back" title="返回高级功能">← 高级</button>' +
				'<button type="button" id="cb-adv-menu" title="显示/隐藏模块菜单">菜单</button>' +
				'<button type="button" id="cb-nav-back" title="返回（Alt+←）">‹ 返回</button>' +
				'<button type="button" id="cb-nav-forward" title="前进（Alt+→）">前进 ›</button>';
			wrap.addEventListener("click", function (e) {
				var btn = e.target.closest ? e.target.closest("button") : null;
				if (!btn) return;
				if (btn.id === "cb-nav-home") {
					window.location.href = "/desk/cb-erp/" + encodeURIComponent("巴西机电erp系统测试");
				} else if (btn.id === "cb-adv-back") {
					window.location.href = "/desk/cb-erp/mep-advanced";
				} else if (btn.id === "cb-adv-menu") {
					window.__cbShowMenu = !window.__cbShowMenu;
					document.body.classList.toggle("cb-focus-mode", !window.__cbShowMenu);
					btn.textContent = window.__cbShowMenu ? "隐藏菜单" : "菜单";
				} else if (btn.id === "cb-nav-back") go(-1);
				else if (btn.id === "cb-nav-forward") go(1);
			});
		}
		if (wrap.parentElement !== title) {
			title.insertBefore(wrap, title.firstChild);
		}
		update();
		applyFocus();
	}

	function start() {
		build();
		try {
			if (frappe.router && frappe.router.on) {
				frappe.router.on("change", function () {
					push(route());
					build();
				});
			}
			$(document).on("page-change", function () {
				push(route());
				build();
			});
		} catch (e) {}
		push(route());

		// 统一品牌显示：旧系统名/CB → MEP
	function brandTitle() {
		try {
			var t = document.title || "";
			var n = t
				.split("巴西机电ERP系统测试").join("MEP 工作台")
				.split("CB 工作台").join("MEP 工作台")
				.split("CB ERP").join("MEP 工作台");
			if (n !== t) document.title = n;
		} catch (e) {}
	}
	brandTitle();
	setInterval(brandTitle, 900);

	document.addEventListener("keydown", function (e) {
			if (!e.altKey) return;
			if (e.key === "ArrowLeft") {
				e.preventDefault();
				go(-1);
			} else if (e.key === "ArrowRight") {
				e.preventDefault();
				go(1);
			}
		});

		var n = 0;
		var timer = setInterval(function () {
			build();
			if (++n > 40) clearInterval(timer);
		}, 800);
		if (window.MutationObserver && document.body) {
			new MutationObserver(build).observe(document.body, { childList: true });
		}
	}

	if (document.readyState === "loading") {
		document.addEventListener("DOMContentLoaded", start);
	} else {
		start();
	}
})();
