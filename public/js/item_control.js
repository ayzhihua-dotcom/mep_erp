// 物料树：批量设置「受控 / 非受控」（Item 列表页按钮）
(function () {
	function esc(s) {
		return frappe.utils.escape_html(s == null ? "" : s);
	}

	function node_html(g) {
		return (
			'<div class="cb-ic-node" data-name="' + esc(g.name) + '" data-group="' + (g.is_group ? 1 : 0) + '">' +
			'<input type="checkbox" class="cb-ic-chk">' +
			'<span class="cb-ic-toggle">' + (g.is_group ? "▸" : "") + "</span>" +
			'<span class="cb-ic-label">' + esc(g.name) + "</span>" +
			'<span class="cb-ic-count">' + (g.count || 0) + "</span>" +
			'<div class="cb-ic-kids"></div>' +
			"</div>"
		);
	}

	function openDialog() {
		var html =
			'<div class="cb-ictl">' +
			'<div class="cb-ictl-tip">勾选分类（可勾父级=整棵子树），然后选择设为受控或非受控。<b>受控</b>=强控设计量/预算；<b>非受控</b>=辅材/耗材，从项目库存放行。</div>' +
			'<div class="cb-ictl-tree" style="max-height:420px;overflow:auto;border:1px solid #e2e8f0;border-radius:8px;padding:6px"></div>' +
			'<div style="margin-top:10px;display:flex;gap:8px">' +
			'<button type="button" class="btn btn-sm btn-primary cb-ic-set1">设为受控</button>' +
			'<button type="button" class="btn btn-sm btn-default cb-ic-set0">设为非受控</button>' +
			'<button type="button" class="btn btn-sm btn-default cb-ic-clear">清空勾选</button>' +
			"</div></div>";
		var d = new frappe.ui.Dialog({
			title: "物料树 · 批量设置受控",
			size: "large",
			fields: [{ fieldtype: "HTML", fieldname: "body", options: html }],
		});
		d.show();
		var $w = d.fields_dict.body.$wrapper;
		var $tree = $w.find(".cb-ictl-tree");

		function load(parent, $box) {
			frappe.call({
				method: "cb_erp.cb_erp.bulk_ops.api_item_tree",
				args: { parent: parent || "" },
				callback: function (r) {
					var groups = r.message || [];
					$box.html(groups.map(node_html).join("") || '<div class="cb-empty">无分类</div>');
				},
			});
		}
		load("", $tree);

		$tree.on("click", ".cb-ic-toggle", function (e) {
			e.stopPropagation();
			var $n = $(this).closest(".cb-ic-node");
			if ($n.attr("data-group") !== "1") return;
			var $kids = $n.find("> .cb-ic-kids").first();
			var loaded = $kids.data("loaded");
			$(this).text(loaded ? "▸" : "▾");
			if (!loaded) {
				$kids.data("loaded", 1);
				load($n.attr("data-name"), $kids);
			} else {
				$kids.toggle();
			}
		});

		$tree.on("change", ".cb-ic-chk", function (e) {
			e.stopPropagation();
			var $n = $(this).closest(".cb-ic-node");
			var on = this.checked;
			$n.find(".cb-ic-chk").each(function () {
				if (this !== e.target) this.checked = on;
			});
			// 父级联动：有勾选则父级勾上
			$n.parents(".cb-ic-node").each(function () {
				$(this).find("> .cb-ic-chk").first().prop("checked", true);
			});
		});

		function collect() {
			var names = [];
			$tree.find(".cb-ic-node").each(function () {
				var $n = $(this);
				if ($n.find("> .cb-ic-chk").first().prop("checked")) names.push($n.attr("data-name"));
			});
			return names;
		}

		function apply(val) {
			var groups = collect();
			if (!groups.length) {
				frappe.msgprint("请先勾选至少一个分类。");
				return;
			}
			frappe.confirm("将所选分类（含子分类）下的物料设为「" + (val ? "受控" : "非受控") + "」？", function () {
				frappe.call({
					method: "cb_erp.cb_erp.bulk_ops.api_set_groups_controlled",
					args: { groups: groups, controlled: val },
					freeze: true,
					callback: function (r) {
						var m = r.message || {};
						frappe.show_alert({
							message: "已更新 " + (m.items || 0) + " 个物料（" + (m.groups || 0) + " 个分类）",
							indicator: "green",
						});
						d.hide();
					},
				});
			});
		}

		$w.find(".cb-ic-set1").on("click", function () {
			apply(1);
		});
		$w.find(".cb-ic-set0").on("click", function () {
			apply(0);
		});
		$w.find(".cb-ic-clear").on("click", function () {
			$tree.find(".cb-ic-chk").prop("checked", false);
		});
	}

	function attach(listview) {
		if (!listview || !listview.page || listview.__cb_ic) return;
		listview.__cb_ic = 1;
		listview.page.add_inner_button("批量设置受控", openDialog);
	}

	try {
		var s = (frappe.listview_settings["Item"] = frappe.listview_settings["Item"] || {});
		var old = s.onload;
		s.onload = function (listview) {
			if (old) old(listview);
			attach(listview);
		};
		// 已缓存设置时兜底
		$(document).on("page-change", function () {
			if (cur_list && cur_list.doctype === "Item") attach(cur_list);
		});
		setInterval(function () {
			try {
				if (typeof cur_list !== "undefined" && cur_list && cur_list.doctype === "Item") attach(cur_list);
			} catch (e) {}
		}, 800);
	} catch (e) {}
})();
