// 专业 / 系统 联动：
// 1) 10 类单据：系统下拉只显示所选专业下的系统；切换专业自动清空系统
// 2) 项目：子表行内联动 + 一键载入标准专业与系统
(function () {
	const DTS = [
		"Material Request", "Purchase Order", "Stock Entry", "Stock Reconciliation",
		"Material Budget", "Material Commitment", "Design BOM", "Design Change Request",
		"CB Shipment", "CB Import Case", "Purchase Receipt", "Quality Inspection",
	];

	DTS.forEach(function (dt) {
		frappe.ui.form.on(dt, {
			setup: function (frm) { bind_disc_query(frm); },
			refresh: function (frm) { bind_disc_query(frm); },
			custom_discipline: function (frm) {
				frm.set_value("custom_system", "");
			},
		});
	});

	function bind_disc_query(frm) {
		if (!frm.fields_dict || !frm.fields_dict.custom_system) return;
		frm.set_query("custom_discipline", function () {
			return { filters: { enabled: 1 } };
		});
		frm.set_query("custom_system", function () {
			return { filters: { discipline: frm.doc.custom_discipline || "" } };
		});
	}

	frappe.ui.form.on("Project", {
		refresh: function (frm) {
			setup_project_grid(frm);
			if (frm.is_new()) {
				frm.add_custom_button("载入标准专业与系统", function () {
					load_standard(frm);
				});
			} else {
				frm.add_custom_button("载入标准专业与系统", function () {
					load_standard(frm);
				});
			}
		},
	});

	frappe.ui.form.on("CB Project System", {
		discipline: function (frm, cdt, cdn) {
			frappe.model.set_value(cdt, cdn, "system", "");
		},
		system: function (frm, cdt, cdn) {
			const row = locals[cdt][cdn];
			if (!row.system) return;
			frappe.db.get_value("CB System", row.system, "discipline").then(function (r) {
				const d = r && r.message && r.message.discipline;
				if (d && d !== row.discipline) {
					frappe.model.set_value(cdt, cdn, "discipline", d);
				}
			});
		},
	});

	function setup_project_grid(frm) {
		if (!frm.fields_dict || !frm.fields_dict.custom_project_systems) return;
		const grid = frm.fields_dict.custom_project_systems.grid;
		grid.get_field("discipline").get_query = function () {
			return { filters: { enabled: 1 } };
		};
		grid.get_field("system").get_query = function (doc, cdt, cdn) {
			const row = locals[cdt][cdn] || {};
			return { filters: { discipline: row.discipline || "" } };
		};
	}

	function load_standard(frm) {
		frappe.call({
			method: "cb_erp.cb_erp.disc_validate.load_standard_systems",
			freeze: true,
			callback: function (r) {
				const rows = r.message || [];
				if (!rows.length) {
					frappe.msgprint("没有可用的专业/系统主数据");
					return;
				}
				const existing = {};
				(frm.doc.custom_project_systems || []).forEach(function (d) {
					existing[d.discipline + "|" + d.system] = 1;
				});
				let added = 0;
				rows.forEach(function (s) {
					const key = s.discipline + "|" + s.name;
					if (existing[key]) return;
					const child = frm.add_child("custom_project_systems");
					child.discipline = s.discipline;
					child.system = s.name;
					added++;
				});
				frm.refresh_field("custom_project_systems");
				frappe.show_alert({ message: "已载入 " + added + " 条专业/系统", indicator: "green" });
			},
		});
	}
})();
