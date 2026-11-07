// 专业 / 系统 / 责任人：可视化选择弹窗（修复 awesomplete 下拉不显示的问题）
// 字段旁提供「选择」，点击空字段也会直接弹出选择器；仍保留手工输入能力。
(function () {
	var FIELDS = {
		custom_discipline: { doctype: "CB Discipline", label: "选择专业", name_field: "discipline_name" },
		custom_system: { doctype: "CB System", label: "选择系统", name_field: "system_name" },
		custom_responsible: { doctype: "User", label: "选择责任人", name_field: "full_name" },
	};

	function esc(s) {
		return frappe.utils.escape_html(s == null ? "" : s);
	}

	function fetch_options(frm, fn, cb) {
		var cfg = FIELDS[fn];
		var args = { doctype: cfg.doctype, limit_page_length: 0 };
		if (cfg.doctype === "User") {
			args.fields = ["name", "full_name"];
			args.filters = { enabled: 1 };
			args.limit_page_length = 500;
		} else {
			args.fields = ["name", cfg.name_field].concat(cfg.doctype === "CB System" ? ["discipline"] : []);
			if (cfg.doctype === "CB System") {
				var disc = frm.doc.custom_discipline;
				if (disc) args.filters = { discipline: disc };
			}
		}
		frappe.call({
			method: "frappe.client.get_list",
			args: args,
			callback: function (r) {
				cb(r.message || []);
			},
			error: function () {
				cb([]);
			},
		});
	}

	function open(frm, fn) {
		var cfg = FIELDS[fn];
		var options = [];
		var html =
			'<div class="cb-linkpick">' +
			'<input class="form-control cb-lp-kw" placeholder="输入关键字筛选…" style="margin-bottom:10px">' +
			'<div class="cb-lp-list" style="max-height:340px;overflow:auto;border:1px solid #e2e8f0;border-radius:8px"></div>' +
			'<div style="margin-top:10px;text-align:right">' +
			'<button type="button" class="btn btn-xs btn-default cb-lp-clear">清除当前值</button>' +
			"</div></div>";
		var d = new frappe.ui.Dialog({
			title: cfg.label,
			size: "small",
			fields: [{ fieldtype: "HTML", fieldname: "body", options: html }],
		});
		d.show();
		var $w = d.fields_dict.body.$wrapper;
		var $list = $w.find(".cb-lp-list");
		var $kw = $w.find(".cb-lp-kw");

		function render() {
			var kw = ($kw.val() || "").toLowerCase();
			var rows = options.filter(function (o) {
				var txt = (o.name + " " + (o[cfg.name_field] || "") + " " + (o.discipline || "")).toLowerCase();
				return !kw || txt.indexOf(kw) >= 0;
			});
			if (!rows.length) {
				$list.html('<div style="padding:14px;color:#94a3b8;text-align:center">无匹配项</div>');
				return;
			}
			var cur = frm.doc[fn];
			var h = "";
			rows.forEach(function (o) {
				var label = o[cfg.name_field] || o.name;
				var sub = o.name !== label ? '<span style="color:#94a3b8;margin-left:6px">' + esc(o.name) + "</span>" : "";
				if (o.discipline) sub += '<span style="color:#94a3b8;margin-left:6px">· ' + esc(o.discipline) + "</span>";
				h +=
					'<button type="button" class="btn btn-default cb-lp-item" data-value="' + esc(o.name) + '"' +
					' style="display:block;width:100%;text-align:left;border:0;border-bottom:1px solid #f1f5f9;border-radius:0;padding:9px 12px' +
					(o.name === cur ? ";background:#eff6ff;font-weight:600" : "") + '">' +
					esc(label) + sub + "</button>";
			});
			$list.html(h);
		}

		$list.on("click", ".cb-lp-item", function () {
			frm.set_value(fn, $(this).attr("data-value"));
			frm.dirty();
			d.hide();
		});
		$kw.on("input", render);
		$w.find(".cb-lp-clear").on("click", function () {
			frm.set_value(fn, "");
			d.hide();
		});

		$list.html('<div style="padding:14px;color:#94a3b8;text-align:center">加载中…</div>');
		fetch_options(frm, fn, function (opts) {
			options = opts;
			render();
		});
	}

	function attach(frm) {
		if (!frm || !frm.fields_dict) return;
		Object.keys(FIELDS).forEach(function (fn) {
			var f = frm.fields_dict[fn];
			if (!f) return;
			var $w = f.$wrapper;
			var $lbl = $w.find(".control-label").first();
			if ($lbl.length && !$lbl.find(".cb-pick-link").length) {
				$lbl.append(' <a class="cb-pick-link" href="#" title="打开选择器">选择</a>');
			}
			$w.off("click.cbpick", ".cb-pick-link").on("click.cbpick", ".cb-pick-link", function (e) {
				e.preventDefault();
				open(frm, fn);
			});
			var input = f.$input && f.$input.get(0);
			if (input && !input.__cbPickBound) {
				input.__cbPickBound = 1;
				input.addEventListener("mousedown", function (e) {
					if (!input.value) {
						e.preventDefault();
						open(cur_frm, fn);
					}
				});
			}
			// 专业变化后，已选系统若不属于该专业则清空
			if (fn === "custom_discipline") {
				f.$input.off("change.cbpick").on("change.cbpick", function () {
					var sys = frm.doc.custom_system;
					if (!sys) return;
					frappe.db.get_value("CB System", sys, "discipline").then(function (r) {
						var d = r.message && r.message.discipline;
						if (d && d !== frm.doc.custom_discipline) frm.set_value("custom_system", "");
					});
				});
			}
		});
	}

	// 覆盖所有表单（Frappe 无 * 通配处理器）：轮询 + 路由变化
	var last_frm = null;
	function tick() {
		try {
			if (typeof cur_frm !== "undefined" && cur_frm) {
				if (cur_frm !== last_frm) {
					last_frm = cur_frm;
					attach(cur_frm);
				} else if (cur_frm.fields_dict && cur_frm.fields_dict.custom_discipline &&
					!cur_frm.fields_dict.custom_discipline.$wrapper.find(".cb-pick-link").length) {
					attach(cur_frm);
				}
			}
		} catch (e) {}
	}
	setInterval(tick, 700);
	tick();
})();
