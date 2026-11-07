// 操作台：大按钮 + 图标 + 说明（挂在 app_include_js，页面记录为 ops-console）
frappe.pages["ops-console"] = frappe.pages["ops-console"] || {};
frappe.pages["ops-console"].on_page_load = function (wrapper) {
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __("操作台"),
		single_column: true,
	});

	const ACTIONS = [
		{
			title: "物料领用（出库）",
			desc: "按项目领用物料，选物料一键生成领料出库单",
			icon: "📤",
			accent: "#f97316",
			group: "库存操作",
			run: () => window.CBOps && CBOps.goto("物料领用"),
		},
		{
			title: "物料入库",
			desc: "采购到货 / 现场入库登记，批量选择物料入库",
			icon: "📥",
			accent: "#10b981",
			group: "库存操作",
			run: () => window.CBOps && CBOps.goto("到货入库"),
		},
		{
			title: "物料退料",
			desc: "批量退回未使用物料，冲减项目领用",
			icon: "↩️",
			accent: "#8b5cf6",
			group: "库存操作",
			run: () => window.CBOps && CBOps.goto("物料退料"),
		},
		{
			title: "库存盘点",
			desc: "现场清点，批量录入盘点后生成盘点差异单",
			icon: "📋",
			accent: "#06b6d4",
			group: "库存操作",
			run: () => window.CBOps && CBOps.goto("库存盘点"),
		},
		{
			title: "批量录入",
			desc: "粘贴表格或 Excel 一次生成多张单据",
			icon: "⚡",
			accent: "#ec4899",
			group: "快速录入",
			run: () => frappe.new_doc("Bulk Entry"),
		},
		{
			title: "采购申请",
			desc: "发起材料采购需求（需选择项目/专业）",
			icon: "📝",
			accent: "#2563eb",
			group: "采购流程",
			run: () => window.CBOps && CBOps.goto("采购申请"),
		},
		{
			title: "采购订单",
			desc: "向供应商下单，关联预算与项目",
			icon: "🛒",
			accent: "#6366f1",
			group: "采购流程",
			run: () => window.CBOps && CBOps.goto("采购订单"),
		},
		{
			title: "采购入库",
			desc: "到货验收后入库，触发质检门控",
			icon: "🏭",
			accent: "#0ea5e9",
			group: "采购流程",
			run: () => window.CBOps && CBOps.goto("到货入库"),
		},
		{
			title: "专业系统矩阵",
			desc: "按专业/系统查看各项目执行量",
			icon: "📊",
			accent: "#f59e0b",
			group: "项目看板",
			run: () => frappe.set_route("query-report", "项目专业系统矩阵"),
		},
		{
			title: "项目总览",
			desc: "进度 / 预算 / 采购 / 出库一屏掌握",
			icon: "🗂️",
			accent: "#14b8a6",
			group: "项目看板",
			run: () => frappe.set_route("query-report", "项目总览"),
		},
		{
			title: "项目文档台账",
			desc: "全部单据按项目归档查看",
			icon: "📚",
			accent: "#64748b",
			group: "项目看板",
			run: () => frappe.set_route("query-report", "项目文档台账"),
		},
		{
			title: "物料明细（九列）",
			desc: "序号/编码/名称/规格/单位/数量/项目/责任人/备注",
			icon: "🧾",
			accent: "#a855f7",
			group: "项目看板",
			run: () => frappe.set_route("query-report", "物料明细（九列）"),
		},
	];

	const groups = [...new Set(ACTIONS.map((a) => a.group))];
	const section = (g) => {
		const items = ACTIONS.filter((a) => a.group === g);
		return `
		<div class="cb-ops-group">
			<div class="cb-ops-group-title">${g}</div>
			<div class="cb-ops-grid">
				${items
					.map(
						(a, i) => `
					<div class="cb-ops-card" data-group="${g}" data-idx="${ACTIONS.indexOf(a)}" style="--accent:${a.accent}">
						<div class="cb-ops-icon">${a.icon}</div>
						<div class="cb-ops-body">
							<div class="cb-ops-title">${a.title}</div>
							<div class="cb-ops-desc">${a.desc}</div>
						</div>
						<div class="cb-ops-arrow">→</div>
					</div>`
					)
					.join("")}
			</div>
		</div>`;
	};

	const html = `
	<div class="cb-ops">
		<div class="cb-ops-hero">
			<div class="cb-ops-hero-text">
				<div class="cb-ops-hero-title">今天要做什么？</div>
				<div class="cb-ops-hero-sub">常用业务一键直达，所有单据都会带专业 / 系统，项目可追溯</div>
			</div>
			<div class="cb-ops-hero-badge">MEP · 项目管理</div>
		</div>
		${groups.map(section).join("")}
	</div>`;

	$(page.body).html(html);

	$(page.body)
		.find(".cb-ops-card")
		.on("click", function () {
			const idx = parseInt($(this).attr("data-idx"), 10);
			const action = ACTIONS[idx];
			if (action && action.run) action.run();
		});
};

frappe.pages["ops-console"].on_page_show = function () {};
