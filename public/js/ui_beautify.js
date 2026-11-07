// 工作台卡片链接彩色图标（纯前端装饰，不改数据）
(function () {
	const MAP = {
		"操作台": "🎛️",
		"批量录入": "⚡",
		"采购申请": "📝",
		"采购订单": "🛒",
		"采购入库": "📦",
		"物料领用/退料": "📤",
		"物料领用（出库）": "📤",
		"库存盘点": "📋",
		"专业系统矩阵": "📊",
		"设计BOM": "📐",
		"设计 BOM": "📐",
		"设计变更申请": "✏️",
		"材料预算": "🧮",
		"材料承诺": "📋",
		"询价单": "🔍",
		"供应商报价": "🤝",
		"材料承诺台账": "📋",
		"装运管理": "🚚",
		"进口案件": "🌐",
		"成本审计日志": "🧾",
		"进口费用分摊": "💰",
		"质检单": "✅",
		"库存收发": "📦",
		"物料": "📦",
		"供应商": "🤝",
		"项目": "📁",
		"专业": "🎓",
		"系统": "🧩",
		"项目视图": "📊",
		"项目任务": "✅",
		"项目预警": "⚠️",
		"预警规则": "⚙️",
		"项目文档台账": "📚",
		"项目总览": "📈",
		"物料分类": "🗂️",
		"主页": "🏠",
		"数据面板": "🕸️",
		"仓库": "🏬",
		"库存移动": "🔁",
		"装运明细": "📃",
		"分摊费用行": "💵",
		"分摊明细": "🧷",
		"进口单证清单": "📑",
		"物料领用（出库）": "📤",
		"物料退料（批量）": "♻️",
		"物料入库": "📥",
		"库存盘点（新建）": "📋",
		"销售出库": "📨",
		"物料凭证": "📄",
		"采购": "🛒",
		"库存": "📥",
		"CB": "🛫",
		"质量": "🔍",
		"业务汇总（专业/系统/责任人）": "📊",
		"物料明细（九列）": "🧾",
	};

	// 分区（工作台七个分组卡）专属图标与主题色：标题 → { icon, color }
	const GRP = {
		"业务操作": { icon: "🎛️", color: "#f97316" },
		"工程与预算": { icon: "📐", color: "#0ea5e9" },
		"采购与承诺": { icon: "🛒", color: "#f59e0b" },
		"物流与进口": { icon: "🚢", color: "#8b5cf6" },
		"质检与库存": { icon: "📦", color: "#10b981" },
		"主数据": { icon: "🧱", color: "#6366f1" },
		"自定义文档": { icon: "📄", color: "#64748b" },
	};

	function decorateGroups() {
		document.querySelectorAll(".links-widget-box").forEach(function (card) {
			const titleEl = card.querySelector(".widget-title .ellipsis") || card.querySelector(".widget-title");
			if (!titleEl) return;
			const name = (titleEl.textContent || "").trim();
			const cfg = GRP[name];
			if (cfg) {
				card.style.setProperty("--grp-c", cfg.color);
				if (!titleEl.dataset.cbGrp) {
					const s = document.createElement("span");
					s.className = "cb-grp-emoji";
					s.textContent = cfg.icon;
					s.style.color = cfg.color;
					titleEl.insertBefore(s, titleEl.firstChild);
					titleEl.dataset.cbGrp = "1";
				}
			}
		});
	}

	function decorate() {
		const nodes = document.querySelectorAll(".link-item, .workspace-link");
		nodes.forEach(function (el) {
			if (el.dataset.cbEmoji) return;
			const text = (el.textContent || "").trim().split("\n")[0].trim();
			if (!text) return;
			// 匹配则用专属 emoji，否则用首字做彩色字标兜底
			const emoji = MAP[text];
			const span = document.createElement("span");
			span.className = emoji ? "cb-emoji" : "cb-emoji cb-emoji-fallback";
			span.textContent = emoji || text.charAt(0);
			el.insertBefore(span, el.firstChild);
			el.dataset.cbEmoji = "1";
		});
	}

	function start() {
		decorate();
		decorateGroups();
		let n = 0;
		const timer = setInterval(function () {
			decorate();
			decorateGroups();
			if (++n > 30) clearInterval(timer);
		}, 1200);
		document.addEventListener("click", function () { setTimeout(decorate, 600); }, true);
		if (window.MutationObserver && document.body) {
			let t = null;
			const obs = new MutationObserver(function () {
				clearTimeout(t);
				t = setTimeout(function () { decorate(); decorateGroups(); }, 400);
			});
			obs.observe(document.body, { childList: true, subtree: true });
		}
	}

	if (document.readyState === "loading") {
		document.addEventListener("DOMContentLoaded", start);
	} else {
		start();
	}
})();
