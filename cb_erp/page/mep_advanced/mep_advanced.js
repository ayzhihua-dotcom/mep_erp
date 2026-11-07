// 高级功能：ERPNext 深度查询与设置（日常请回 MEP 工作台）
frappe.pages["mep-advanced"] = frappe.pages["mep-advanced"] || {};

frappe.pages["mep-advanced"].on_page_load = function (wrapper) {
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __("高级功能"),
		single_column: true,
	});

	const GROUPS = [
		{
			label: "库存深度",
			icon: "🏬",
			color: "#2563eb",
			items: [
				{ t: "库存余额（项目）", d: "按项目/专业查看到货、领用与结存", r: ["query-report", "MEP 项目库存余额"] },
				{ t: "物料流水", d: "按项目/物料/仓库查收发存明细", r: ["query-report", "MEP 物料流水"] },
				{ t: "仓库库存余额", d: "ERPNext 标准库存余额", r: ["query-report", "Stock Balance"] },
				{ t: "库龄", d: "按物料/仓库查看库存库龄", r: ["query-report", "Stock Ageing"] },
				{ t: "可用数量", d: "预计可用数量（含在途/预留）", r: ["query-report", "Stock Projected Qty"] },
				{ t: "批次 / 序列号", d: "序列号与批次追踪", r: ["List", "Serial No"] },
			],
		},
		{
			label: "采购深度",
			icon: "🛒",
			color: "#d97706",
			items: [
				{ t: "采购订单列表", d: "全部采购订单（含筛选/导出）", r: ["List", "Purchase Order"] },
				{ t: "采购申请列表", d: "全部采购申请", r: ["List", "Material Request"] },
				{ t: "询价单", d: "向供应商询价", r: ["List", "Request for Quotation"] },
				{ t: "供应商报价", d: "供应商报价与比价", r: ["List", "Supplier Quotation"] },
				{ t: "采购与领用台账", d: "按项目/专业/类型/日期查采购与领用", r: ["query-report", "采购与领用台账"] },
			],
		},
		{
			label: "质量深度",
			icon: "🛡️",
			color: "#7c3aed",
			items: [
				{ t: "质检单", d: "全部质检单（含项目/状态）", r: ["List", "Quality Inspection"] },
				{ t: "质检模板", d: "质检项目与标准", r: ["List", "Quality Inspection Template"] },
				{ t: "不合格报告（NCR）", d: "不合格报告与整改", r: ["List", "CB NCR"] },
				{ t: "项目文档台账", d: "资料、NCR、试运行等汇总", r: ["query-report", "项目文档台账"] },
			],
		},
		{
			label: "项目深度",
			icon: "📁",
			color: "#0891b2",
			items: [
				{ t: "项目列表", d: "全部项目（含状态/进度）", r: ["List", "Project"] },
				{ t: "任务", d: "项目任务与进度", r: ["List", "Task"] },
				{ t: "项目库存消耗", d: "项目维度库存消耗", r: ["query-report", "Project wise Stock Tracking"] },
				{ t: "项目总览", d: "进度 / 预算 / 采购 / 出库", r: ["query-report", "项目总览"] },
			],
		},
		{
			label: "主数据与设置",
			icon: "🗄️",
			color: "#475569",
			items: [
				{ t: "物料", d: "物料主数据与分类", r: ["List", "Item"] },
				{ t: "供应商", d: "供应商主数据", r: ["List", "Supplier"] },
				{ t: "仓库", d: "仓库与库位", r: ["List", "Warehouse"] },
				{ t: "用户", d: "用户与权限", r: ["List", "User"] },
				{ t: "系统设置", d: "全局系统参数", r: ["Form", "System Settings"] },
			],
		},
		{
			label: "账号与流程（管理员）",
			icon: "🔐",
			color: "#be123c",
			adminOnly: true,
			items: [
				{ t: "用户", d: "新建账号、启停用、分配角色", r: ["List", "User"] },
				{ t: "角色", d: "角色定义（岗位职责的基础）", r: ["List", "Role"] },
				{ t: "岗位 / 角色模板", d: "一套角色打包成岗位", r: ["List", "Role Profile"] },
				{ t: "角色权限管理", d: "按角色分配单据增删改查/提交/报表权限", r: ["permission-manager"] },
				{ t: "用户权限限制", d: "限制用户只能看某个项目/仓库/公司", r: ["List", "User Permission"] },
				{ t: "页面与报表权限", d: "控制页面、报表对哪些角色开放", r: ["List", "Role Permission for Page and Report"] },
				{ t: "工作流", d: "审批状态、动作、允许角色", r: ["List", "Workflow"] },
				{ t: "工作流状态", d: "草稿/待审/已批准等状态", r: ["List", "Workflow State"] },
				{ t: "通知", d: "审批/预警消息通知", r: ["List", "Notification"] },
				{ t: "分配规则", d: "按条件自动分配给责任人", r: ["List", "Assignment Rule"] },
				{ t: "系统设置", d: "全局参数与默认值", r: ["Form", "System Settings"] },
				{ t: "备份", d: "站点备份与恢复", r: ["backups"] },
			],
		},
	];

	const IS_ADMIN =
		(frappe.user.has_role && (frappe.user.has_role("System Manager") || frappe.user.has_role("SYS 系统管理员")));
	const VISIBLE_GROUPS = GROUPS.filter((g) => !g.adminOnly || IS_ADMIN);

	const card = (it) =>
		`<button type="button" class="cb-adv-card" data-route='${JSON.stringify(it.r)}'>
			<div class="cb-adv-card-t">${frappe.utils.escape_html(it.t)}</div>
			<div class="cb-adv-card-d">${frappe.utils.escape_html(it.d)}</div>
		</button>`;

	const html = `
	<div class="cb-adv">
		<div class="cb-adv-hero">
			<div>
				<div class="cb-adv-hero-t">高级功能</div>
				<div class="cb-adv-hero-d">这里放 ERPNext 的深度查询与设置；日常录入、台账、项目执行请回 MEP 工作台。</div>
			</div>
			<button type="button" class="btn btn-sm btn-primary cb-adv-home">⌂ 返回 MEP 工作台</button>
		</div>
		<input class="form-control cb-adv-search" placeholder="搜索功能，例如：库存、质检、采购订单、系统设置…">
		<div class="cb-adv-groups">
			${VISIBLE_GROUPS.map(
				(g) => `
				<div class="cb-adv-group" style="--grp:${g.color}">
					<div class="cb-adv-group-h"><span>${g.icon}</span>${g.label}</div>
					<div class="cb-adv-grid">${g.items.map(card).join("")}</div>
				</div>`
			).join("")}
		</div>
		<div class="cb-adv-empty" style="display:none">没有匹配的功能</div>
	</div>`;

	$(page.body).html(html);

	$(page.body).on("click", ".cb-adv-card", function () {
		try {
			const r = JSON.parse($(this).attr("data-route"));
			frappe.set_route.apply(null, r);
		} catch (e) {}
	});
	$(page.body).on("click", ".cb-adv-home", function () {
		window.location.href = "/desk/cb-erp/" + encodeURIComponent("巴西机电erp系统测试");
	});
	$(page.body).on("input", ".cb-adv-search", function () {
		const kw = ($(this).val() || "").toLowerCase().trim();
		let shown = 0;
		$(page.body)
			.find(".cb-adv-group")
			.each(function () {
				let n = 0;
				$(this)
					.find(".cb-adv-card")
					.each(function () {
						const txt = ($(this).text() || "").toLowerCase();
						const ok = !kw || txt.indexOf(kw) >= 0;
						$(this).toggle(ok);
						if (ok) n++;
					});
				$(this).toggle(n > 0);
				shown += n;
			});
		$(page.body).find(".cb-adv-empty").toggle(shown === 0);
	});
};

frappe.pages["mep-advanced"].on_page_show = function () {};
