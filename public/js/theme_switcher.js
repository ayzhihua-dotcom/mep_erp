// 主题切换器：右下角 🎨，6 套配色，选择后记忆
(function () {
	const KEY = "cb_theme";
	const THEMES = [
		{ id: "ocean", name: "科技蓝", c1: "#2563eb", c2: "#0ea5e9" },
		{ id: "emerald", name: "翡翠绿", c1: "#059669", c2: "#34d399" },
		{ id: "sunset", name: "日落橙", c1: "#ea580c", c2: "#fb923c" },
		{ id: "violet", name: "星云紫", c1: "#7c3aed", c2: "#a78bfa" },
		{ id: "rose", name: "玫瑰红", c1: "#e11d48", c2: "#fb7185" },
		{ id: "midnight", name: "暗夜蓝", c1: "#0b1220", c2: "#38bdf8" },
		{ id: "china", name: "中国红", c1: "#b91c1c", c2: "#ef4444" },
	];

	function apply(id) {
		document.documentElement.setAttribute("data-cb-theme", id);
		try {
			localStorage.setItem(KEY, id);
		} catch (e) {}
		document.querySelectorAll(".cb-theme-item").forEach(function (el) {
			el.classList.toggle("active", el.getAttribute("data-theme") === id);
		});
	}

	// 尽早应用，避免闪烁
	try {
		apply(localStorage.getItem(KEY) || "ocean");
	} catch (e) {
		apply("ocean");
	}

	function build() {
		if (document.querySelector(".cb-theme-fab")) return;
		if (!document.body) return;

		const fab = document.createElement("div");
		fab.className = "cb-theme-fab";
		fab.title = "切换主题";
		fab.innerHTML = "🎨";

		const panel = document.createElement("div");
		panel.className = "cb-theme-panel";
		panel.innerHTML =
			"<h6>界面主题</h6>" +
			THEMES.map(
				(t) =>
					'<div class="cb-theme-item" data-theme="' +
					t.id +
					'"><span class="cb-theme-dot" style="background:linear-gradient(135deg,' +
					t.c1 +
					"," +
					t.c2 +
					')"></span><span class="cb-theme-name">' +
					t.name +
					'</span><span class="cb-theme-check">✓</span></div>'
			).join("");

		document.body.appendChild(fab);
		document.body.appendChild(panel);

		fab.addEventListener("click", function (e) {
			e.stopPropagation();
			panel.classList.toggle("open");
		});
		document.addEventListener("click", function (e) {
			if (!panel.contains(e.target) && e.target !== fab) panel.classList.remove("open");
		});
		panel.querySelectorAll(".cb-theme-item").forEach(function (el) {
			el.addEventListener("click", function () {
				apply(el.getAttribute("data-theme"));
				panel.classList.remove("open");
				if (window.frappe && frappe.show_alert) {
					frappe.show_alert({ message: "主题已切换：" + el.querySelector(".cb-theme-name").innerText, indicator: "green" }, 2);
				}
			});
		});

		apply(document.documentElement.getAttribute("data-cb-theme") || "ocean");
	}

	if (document.readyState === "loading") {
		document.addEventListener("DOMContentLoaded", build);
	} else {
		build();
	}
	// 桌面端路由切换后可能重建 body 结构，兜底再挂一次
	setTimeout(build, 1200);
})();
