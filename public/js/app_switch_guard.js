// 应用切换兜底：v16 顶部菜单里的「All apps」指向 /apps，而本环境 /apps 会 301 到 /desk，
// 客户端路由 "apps" 又报「页面 apps未找到」，点进去会停在空白页、无法再切回。
// 这里把它改为跳到 ERPNext 主页，保证任何情况下都能回到有侧栏的页面。
(function () {
	const LABELS = ["All apps", "所有应用", "全部应用", "全部应用 "];
	function labelOf(el) {
		return (el && el.textContent ? el.textContent : "").replace(/\s+/g, " ").trim();
	}
	document.addEventListener(
		"click",
		function (e) {
			let el = e.target;
			while (el && el !== document.body) {
				const tag = el.tagName;
				if (tag === "A" || tag === "BUTTON" || el.getAttribute("role") === "menuitem") {
					if (LABELS.indexOf(labelOf(el)) !== -1) {
						e.preventDefault();
						e.stopPropagation();
						window.location.href = "/desk/home";
						return;
					}
				}
				el = el.parentElement;
			}
		},
		true
	);
})();
