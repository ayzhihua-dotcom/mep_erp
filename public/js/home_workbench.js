// ERPNext 主页「整体调布局 + 功能显示」：把首页空白的「损益表」区块替换为 CB 工作台分区入口。
// 纯前端增强，不改数据；链接直接跳到可用的单据列表 / 报表 / 页面。
(function () {
	// 每个分区：标题、图标、主题色、链接（label / 类型 / 目标 / emoji）
	const SECTIONS = [
		{
			label: "业务操作",
			icon: "🎛️",
			color: "#f97316",
			links: [
				{ label: "操作台", type: "page", to: "ops-console", icon: "🎛️" },
				{ label: "批量录入", type: "doctype", to: "Bulk Entry", icon: "⚡" },
				{ label: "采购申请（批量）", type: "ops", kind: "采购申请", icon: "📝" },
				{ label: "采购下单（批量）", type: "ops", kind: "采购订单", icon: "🛒" },
				{ label: "到货入库（批量）", type: "ops", kind: "到货入库", icon: "📥" },
				{ label: "物料领用（批量）", type: "ops", kind: "物料领用", icon: "📤" },
				{ label: "物料退料（批量）", type: "ops", kind: "物料退料", icon: "↩️" },
				{ label: "库存盘点（批量）", type: "ops", kind: "库存盘点", icon: "📋" },
				{ label: "专业系统矩阵", type: "report", to: "项目专业系统矩阵", icon: "📊" },
			],
		},
		{
			label: "工程与预算",
			icon: "📐",
			color: "#0ea5e9",
			links: [
				{ label: "设计 BOM", type: "doctype", to: "Design BOM", icon: "📐" },
				{ label: "设计变更申请", type: "doctype", to: "Design Change Request", icon: "✏️" },
				{ label: "材料预算", type: "doctype", to: "Material Budget", icon: "🧮" },
			],
		},
		{
			label: "采购与承诺",
			icon: "🛒",
			color: "#f59e0b",
			links: [
				{ label: "采购下单追踪", type: "report", to: "采购下单追踪", icon: "🔔" },
				{ label: "采购与领用台账", type: "report", to: "采购与领用台账", icon: "📒" },
				{ label: "采购申请列表", type: "doctype", to: "Material Request", icon: "📝" },
				{ label: "询价单", type: "doctype", to: "Request for Quotation", icon: "🔍" },
				{ label: "供应商报价", type: "doctype", to: "Supplier Quotation", icon: "🤝" },
				{ label: "采购下单", type: "new", to: "Bulk Entry", defaults: { kind: "采购订单" }, icon: "🛒" },
				{ label: "采购订单列表", type: "doctype", to: "Purchase Order", icon: "📄" },
				{ label: "材料承诺台账", type: "doctype", to: "Material Commitment", icon: "📋" },
			],
		},
		{
			label: "物流与进口",
			icon: "🚢",
			color: "#8b5cf6",
			links: [
				{ label: "装运管理", type: "doctype", to: "CB Shipment", icon: "🚚" },
				{ label: "进口案件", type: "doctype", to: "CB Import Case", icon: "🌐" },
			],
		},
		{
			label: "质检与库存",
			icon: "📦",
			color: "#10b981",
			links: [
				{ label: "质检单", type: "doctype", to: "Quality Inspection", icon: "✅" },
				{ label: "不合格报告", type: "doctype", to: "CB NCR", icon: "🚫" },
				{ label: "扫码查询", type: "url", to: "/scan", icon: "📷" },
				{ label: "库存收发列表", type: "doctype", to: "Stock Entry", icon: "🔄" },
				{ label: "到货入库列表", type: "doctype", to: "Purchase Receipt", icon: "📦" },
				{ label: "盘点列表", type: "doctype", to: "Stock Reconciliation", icon: "📋" },
			],
		},
		{
			label: "主数据",
			icon: "🧱",
			color: "#6366f1",
			links: [
				{ label: "物料", type: "doctype", to: "Item", icon: "📦" },
				{ label: "供应商", type: "doctype", to: "Supplier", icon: "🤝" },
				{ label: "项目", type: "doctype", to: "Project", icon: "📁" },
				{ label: "专业", type: "doctype", to: "CB Discipline", icon: "🎓" },
				{ label: "系统", type: "doctype", to: "CB System", icon: "🧩" },
			],
		},
		{
			label: "项目视图",
			icon: "📊",
			color: "#64748b",
			links: [
				{ label: "物资四量台账", type: "report", to: "物资四量台账", icon: "🧮" },
				{ label: "里程碑齐套", type: "report", to: "里程碑齐套检查", icon: "📦" },
				{ label: "实物量进度", type: "report", to: "实物量进度", icon: "📈" },
				{ label: "安装记录", type: "doctype", to: "CB Installation Record", icon: "🔧" },
				{ label: "试运行/移交", type: "doctype", to: "CB Commissioning Record", icon: "🏁" },
				{ label: "项目物料执行台账", type: "report", to: "项目物料执行台账", icon: "📈" },
				{ label: "项目任务", type: "doctype", to: "Task", icon: "✅" },
				{ label: "项目预警", type: "doctype", to: "Alert Event", icon: "⚠️" },
				{ label: "预警规则", type: "doctype", to: "Alert Rule", icon: "⚙️" },
				{ label: "项目文档台账", type: "report", to: "项目文档台账", icon: "📚" },
				{ label: "项目总览", type: "report", to: "项目总览", icon: "📈" },
				{ label: "物料分类", type: "doctype", to: "Item Group", icon: "🗂️" },
				{ label: "业务汇总", type: "report", to: "业务汇总（专业系统责任人）", icon: "📊" },
				{ label: "物料明细（九列）", type: "report", to: "物料明细（九列）", icon: "🧾" },
			],
		},
	];

	function slug(s) {
		return String(s || "")
			.toLowerCase()
			.replace(/[^a-z0-9]+/g, "-")
			.replace(/^-|-$/g, "");
	}

	// 规范列表路由表（/desk/<模块>/<单据>），避免 set_route 生成缺模块前缀的坏路由
	var LIST_ROUTES = {
		"Bulk Entry": "/desk/cb-erp/bulk-entry",
		"Material Request": "/desk/stock/material-request",
		"Purchase Order": "/desk/buying/purchase-order",
		"Purchase Receipt": "/desk/stock/purchase-receipt",
		"Stock Entry": "/desk/stock/stock-entry",
		"Stock Reconciliation": "/desk/stock/stock-reconciliation",
		"Design BOM": "/desk/cb-erp/design-bom",
		"Design Change Request": "/desk/cb-erp/design-change-request",
		"Material Budget": "/desk/cb-erp/material-budget",
		"Material Commitment": "/desk/cb-erp/material-commitment",
		"CB Shipment": "/desk/cb-erp/cb-shipment",
		"CB Import Case": "/desk/cb-erp/cb-import-case",
		"Quality Inspection": "/desk/stock/quality-inspection",
		"CB NCR": "/desk/cb-erp/cb-ncr",
		"Item": "/desk/stock/item",
		"Supplier": "/desk/buying/supplier",
		"Project": "/desk/projects/project",
		"CB Discipline": "/desk/cb-erp/cb-discipline",
		"CB System": "/desk/cb-erp/cb-system",
		"Task": "/desk/projects/task",
		"Alert Event": "/desk/cb-erp/alert-event",
		"Alert Rule": "/desk/cb-erp/alert-rule",
		"Item Group": "/desk/setup/item-group",
		"CB Commissioning Record": "/desk/cb-erp/cb-commissioning-record",
		"CB Installation Record": "/desk/cb-erp/cb-installation-record",
		"Request for Quotation": "/desk/buying/request-for-quotation",
		"Supplier Quotation": "/desk/buying/supplier-quotation",
	};

	function listRoute(dt) {
		if (LIST_ROUTES[dt]) return LIST_ROUTES[dt];
		try {
			var meta = frappe.get_meta(dt);
			var mod = meta && meta.module ? slug(meta.module) : "";
			return "/desk/" + (mod ? mod + "/" : "") + slug(dt);
		} catch (e) {
			return null;
		}
	}

	function go(link) {
		try {
			if (link.type === "url") {
				window.location.href = link.to;
				return;
			}
			if (link.type === "new") {
				if (window.frappe && frappe.new_doc) frappe.new_doc(link.to, link.defaults || {});
				return;
			}
			if (link.type === "ops") {
				if (window.CBOps && CBOps.goto) CBOps.goto(link.kind);
				return;
			}
			if (link.type === "report") {
				if (window.frappe) frappe.set_route("query-report", link.to);
				return;
			}
			if (link.type === "page") {
				if (window.frappe) frappe.set_route(link.to);
				return;
			}
			if (link.type === "doctype") {
				var r = listRoute(link.to);
				if (r) {
					window.location.href = r;
					return;
				}
				if (window.frappe) frappe.set_route("List", link.to);
			}
		} catch (e) {
			/* 忽略 */
		}
	}

	function buildGrid() {
		const wrap = document.createElement("div");
		wrap.className = "cb-home-wb";

		const header = document.createElement("div");
		header.className = "cb-home-wb-header";
		header.innerHTML =
			'<span class="cb-home-wb-emoji">🗂️</span>' +
			'<span class="cb-home-wb-title">MEP 工作台</span>' +
			'<span class="cb-home-wb-sub">业务快捷入口</span>';
		wrap.appendChild(header);

		SECTIONS.forEach(function (sec) {
			const card = document.createElement("div");
			card.className = "cb-wb-section";
			card.style.setProperty("--grp-c", sec.color);

			const h = document.createElement("div");
			h.className = "cb-wb-h";
			const ic = document.createElement("span");
			ic.className = "cb-wb-h-emoji";
			ic.textContent = sec.icon;
			const tx = document.createElement("span");
			tx.className = "cb-wb-h-text";
			tx.textContent = sec.label;
			h.appendChild(ic);
			h.appendChild(tx);
			card.appendChild(h);

			const g = document.createElement("div");
			g.className = "cb-wb-grid";
			sec.links.forEach(function (l) {
				const a = document.createElement("button");
				a.type = "button";
				a.className = "cb-wb-link";
				const e = document.createElement("span");
				e.className = "cb-wb-link-emoji";
				e.textContent = l.icon;
				const t = document.createElement("span");
				t.className = "cb-wb-link-text";
				t.textContent = l.label;
				a.appendChild(e);
				a.appendChild(t);
				a.addEventListener("click", function () {
					go(l);
				});
				g.appendChild(a);
			});
			card.appendChild(g);
			wrap.appendChild(card);
		});
		return wrap;
	}

	function transform() {
		const redactor = document.querySelector(".codex-editor__redactor");
		if (!redactor) return;
		// 只在含有「损益表」主页小部件时处理，避免影响其它页面
		const pnl = redactor.querySelector(".dashboard-widget-box");
		if (!pnl) return;
		const pnlTitleEl = pnl.querySelector(".widget-title .ellipsis, .widget-title");
		const title = pnlTitleEl ? pnlTitleEl.textContent.trim() : "";
		if (title && title !== "损益表") return;

		// 已注入则跳过
		if (redactor.querySelector(".cb-home-wb-block")) return;

		// 隐藏空白损益表区块
		const pnlBlock = pnl.closest(".ce-block");
		if (pnlBlock) pnlBlock.style.display = "none";

		// 注入工作台网格（放在最后，统计卡保持在上方）
		const block = document.createElement("div");
		block.className = "ce-block col-xs-12 cb-home-wb-block";
		const content = document.createElement("div");
		content.className = "ce-block__content";
		content.appendChild(buildGrid());
		block.appendChild(content);
		redactor.appendChild(block);
	}

	function start() {
		transform();
		// 多轮兜底（SPA 异步渲染）
		let n = 0;
		const timer = setInterval(function () {
			transform();
			if (++n > 40) clearInterval(timer);
		}, 800);
		// 路由切换后重新处理
		if (window.frappe && frappe.router && frappe.router.on) {
			frappe.router.on("change", function () {
				setTimeout(transform, 400);
				setTimeout(transform, 1200);
			});
		}
		if (window.MutationObserver && document.body) {
			let t = null;
			const obs = new MutationObserver(function () {
				clearTimeout(t);
				t = setTimeout(transform, 350);
			});
			obs.observe(document.body, { childList: true, subtree: true });
		}
		document.addEventListener("click", function () {
			setTimeout(transform, 600);
		}, true);
	}

	if (document.readyState === "loading") {
		document.addEventListener("DOMContentLoaded", start);
	} else {
		start();
	}
})();
