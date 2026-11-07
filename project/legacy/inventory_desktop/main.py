import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import database as db

class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("出入库管理系统 - 登录")
        self.root.geometry("350x250")
        self.root.resizable(False, False)
        
        # Center window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() - 350) // 2
        y = (self.root.winfo_screenheight() - 250) // 2
        self.root.geometry(f"350x250+{x}+{y}")
        
        # Title
        title_label = tk.Label(root, text="出入库管理系统", font=("微软雅黑", 16, "bold"))
        title_label.pack(pady=20)
        
        # Username
        tk.Label(root, text="用户名:").pack()
        self.username_entry = tk.Entry(root, width=25)
        self.username_entry.pack(pady=5)
        self.username_entry.insert(0, "admin")
        
        # Password
        tk.Label(root, text="密码:").pack()
        self.password_entry = tk.Entry(root, width=25, show="*")
        self.password_entry.pack(pady=5)
        self.password_entry.insert(0, "admin123")
        
        # Login button
        tk.Button(root, text="登录", width=15, command=self.login).pack(pady=20)
        
        self.root.bind('<Return>', lambda e: self.login())
        self.username_entry.focus()
    
    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        if not username or not password:
            messagebox.showerror("错误", "请输入用户名和密码")
            return
        
        user = db.verify_user(username, password)
        if user:
            self.root.destroy()
            main_root = tk.Tk()
            MainWindow(main_root, user)
            main_root.mainloop()
        else:
            messagebox.showerror("错误", "用户名或密码错误")

class MainWindow:
    def __init__(self, root, user):
        self.root = root
        self.user = user
        self.root.title(f"出入库管理系统 - {user['username']}")
        self.root.geometry("1000x650")
        
        # Center window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() - 1000) // 2
        y = (self.root.winfo_screenheight() - 650) // 2
        self.root.geometry(f"1000x650+{x}+{y}")
        
        # Menu bar
        menubar = tk.Menu(root)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="退出登录", command=self.logout)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=root.quit)
        menubar.add_cascade(label="文件", menu=file_menu)
        root.config(menu=menubar)
        
        # Left navigation
        nav_frame = tk.Frame(root, width=180, bg="#2c3e50")
        nav_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        # Logo
        tk.Label(nav_frame, text="📦 出入库管理", bg="#2c3e50", fg="white", 
                font=("微软雅黑", 12, "bold")).pack(pady=20)
        
        # Navigation buttons
        nav_items = [
            ("🏠 仪表盘", self.show_dashboard),
            ("📦 商品管理", self.show_products),
            ("📥 入库管理", self.show_inbound),
            ("📤 出库管理", self.show_outbound),
            ("🔍 库存查询", self.show_stock),
            ("📋 库存盘点", self.show_stocktake),
            ("↩️ 退入库", self.show_returns),
            ("📊 报表统计", self.show_reports),
        ]
        
        if user['role'] == 'admin':
            nav_items.append(("👥 用户管理", self.show_users))
        
        for text, command in nav_items:
            btn = tk.Button(nav_frame, text=text, bg="#34495e", fg="white", 
                           font=("微软雅黑", 10), relief=tk.FLAT, anchor="w",
                           padx=20, pady=10, command=command)
            btn.pack(fill=tk.X, padx=5, pady=2)
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#3d566e"))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg="#34495e"))
        
        # User info at bottom
        tk.Label(nav_frame, text=f"👤 {user['username']}", bg="#2c3e50", fg="white",
                font=("微软雅黑", 9)).pack(side=tk.BOTTOM, pady=10)
        
        # Main content area
        self.content_frame = tk.Frame(root, bg="white")
        self.content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.show_dashboard()
    
    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def show_dashboard(self):
        self.clear_content()
        stats = db.get_dashboard_stats()
        
        # Title
        tk.Label(self.content_frame, text="仪表盘", font=("微软雅黑", 16, "bold"),
                bg="white").pack(pady=20, anchor="w", padx=20)
        
        # Stats cards
        cards_frame = tk.Frame(self.content_frame, bg="white")
        cards_frame.pack(fill=tk.X, padx=20)
        
        card_data = [
            ("商品总数", stats['total_products'], "#3498db"),
            ("库存总值", f"¥{stats['total_value']:.2f}", "#2ecc71"),
            ("库存预警", stats['low_stock'], "#e74c3c"),
            ("今日入库", stats['today_inbound'], "#9b59b6"),
            ("今日出库", stats['today_outbound'], "#f39c12"),
        ]
        
        for i, (title, value, color) in enumerate(card_data):
            card = tk.Frame(cards_frame, bg=color, width=170, height=80)
            card.grid(row=0, column=i, padx=10, pady=10, sticky="nsew")
            cards_frame.columnconfigure(i, weight=1)
            
            tk.Label(card, text=title, bg=color, fg="white", font=("微软雅黑", 10)).pack(pady=(10, 5))
            tk.Label(card, text=str(value), bg=color, fg="white", font=("微软雅黑", 14, "bold")).pack()
        
        # Recent records
        records_frame = tk.Frame(self.content_frame, bg="white")
        records_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Recent inbound
        tk.Label(records_frame, text="最近入库", font=("微软雅黑", 11, "bold"),
                bg="white").pack(anchor="w")
        
        inbound_tree = ttk.Treeview(records_frame, columns=("product", "quantity", "time"), 
                                   show="headings", height=4)
        inbound_tree.heading("product", text="商品")
        inbound_tree.heading("quantity", text="数量")
        inbound_tree.heading("time", text="时间")
        inbound_tree.pack(fill=tk.X, pady=5)
        
        inbound_records = db.get_inbound_records()[:5]
        for r in inbound_records:
            inbound_tree.insert("", "end", values=(r['product_name'], r['quantity'], 
                                                   r['created_at'][:16]))
        
        # Recent outbound
        tk.Label(records_frame, text="最近出库", font=("微软雅黑", 11, "bold"),
                bg="white").pack(anchor="w", pady=(10, 0))
        
        outbound_tree = ttk.Treeview(records_frame, columns=("product", "quantity", "time"), 
                                    show="headings", height=4)
        outbound_tree.heading("product", text="商品")
        outbound_tree.heading("quantity", text="数量")
        outbound_tree.heading("time", text="时间")
        outbound_tree.pack(fill=tk.X, pady=5)
        
        outbound_records = db.get_outbound_records()[:5]
        for r in outbound_records:
            outbound_tree.insert("", "end", values=(r['product_name'], r['quantity'], 
                                                    r['created_at'][:16]))
    
    def show_products(self):
        self.clear_content()
        
        # Title
        title_frame = tk.Frame(self.content_frame, bg="white")
        title_frame.pack(fill=tk.X, padx=20, pady=20)
        
        tk.Label(title_frame, text="商品管理", font=("微软雅黑", 16, "bold"),
                bg="white").pack(side=tk.LEFT)
        
        tk.Button(title_frame, text="➕ 添加商品", command=self.add_product_dialog,
                 bg="#3498db", fg="white", font=("微软雅黑", 10)).pack(side=tk.RIGHT)
        
        # Treeview
        tree_frame = tk.Frame(self.content_frame, bg="white")
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=20)
        
        columns = ("code", "name", "category", "unit", "price", "stock", "min_stock")
        tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)
        
        tree.heading("code", text="编码")
        tree.heading("name", text="名称")
        tree.heading("category", text="分类")
        tree.heading("unit", text="单位")
        tree.heading("price", text="单价")
        tree.heading("stock", text="库存")
        tree.heading("min_stock", text="最低库存")
        
        tree.column("code", width=100)
        tree.column("name", width=150)
        tree.column("category", width=80)
        tree.column("unit", width=60)
        tree.column("price", width=80)
        tree.column("stock", width=80)
        tree.column("min_stock", width=80)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        products = db.get_all_products()
        for p in products:
            tag = "low" if p['stock'] <= p['min_stock'] else ""
            tree.insert("", "end", values=(p['code'], p['name'], p['category'], 
                                          p['unit'], f"¥{p['price']:.2f}", p['stock'], p['min_stock']),
                       tags=(tag,))
        
        tree.tag_configure("low", foreground="red")
        
        # Buttons
        btn_frame = tk.Frame(self.content_frame, bg="white")
        btn_frame.pack(fill=tk.X, padx=20, pady=10)
        
        def edit_selected():
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("提示", "请选择要编辑的商品")
                return
            item = tree.item(selected[0])
            code = item['values'][0]
            product = next((p for p in products if p['code'] == code), None)
            if product:
                self.edit_product_dialog(product)
        
        def delete_selected():
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("提示", "请选择要删除的商品")
                return
            if messagebox.askyesno("确认", "确定要删除此商品吗？"):
                item = tree.item(selected[0])
                code = item['values'][0]
                product = next((p for p in products if p['code'] == code), None)
                if product:
                    db.delete_product(product['id'])
                    self.show_products()
        
        tk.Button(btn_frame, text="编辑", command=edit_selected, bg="#f39c12", fg="white",
                 font=("微软雅黑", 10)).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="删除", command=delete_selected, bg="#e74c3c", fg="white",
                 font=("微软雅黑", 10)).pack(side=tk.LEFT, padx=5)
    
    def add_product_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("添加商品")
        dialog.geometry("350x300")
        dialog.resizable(False, False)
        
        fields = [
            ("编码:", "code"),
            ("名称:", "name"),
            ("分类:", "category"),
            ("单位:", "unit"),
            ("单价:", "price"),
            ("最低库存:", "min_stock"),
        ]
        
        entries = {}
        for i, (label, field) in enumerate(fields):
            tk.Label(dialog, text=label).grid(row=i, column=0, padx=10, pady=5, sticky="e")
            entry = tk.Entry(dialog, width=25)
            entry.grid(row=i, column=1, padx=10, pady=5)
            entries[field] = entry
        
        entries['min_stock'].insert(0, "0")
        
        def save():
            code = entries['code'].get()
            name = entries['name'].get()
            category = entries['category'].get()
            unit = entries['unit'].get()
            price = entries['price'].get()
            min_stock = entries['min_stock'].get()
            
            if not code or not name or not unit or not price:
                messagebox.showerror("错误", "请填写必填项")
                return
            
            try:
                price = float(price)
                min_stock = int(min_stock)
            except ValueError:
                messagebox.showerror("错误", "价格和库存必须是数字")
                return
            
            if db.add_product(code, name, category, unit, price, min_stock):
                messagebox.showinfo("成功", "商品添加成功")
                dialog.destroy()
                self.show_products()
            else:
                messagebox.showerror("错误", "编码已存在")
        
        tk.Button(dialog, text="保存", command=save, bg="#3498db", fg="white",
                 font=("微软雅黑", 10), width=10).grid(row=len(fields), column=0, columnspan=2, pady=20)
    
    def edit_product_dialog(self, product):
        dialog = tk.Toplevel(self.root)
        dialog.title("编辑商品")
        dialog.geometry("350x300")
        dialog.resizable(False, False)
        
        fields = [
            ("编码:", "code", product['code']),
            ("名称:", "name", product['name']),
            ("分类:", "category", product['category'] or ''),
            ("单位:", "unit", product['unit']),
            ("单价:", "price", str(product['price'])),
            ("最低库存:", "min_stock", str(product['min_stock'])),
        ]
        
        entries = {}
        for i, (label, field, value) in enumerate(fields):
            tk.Label(dialog, text=label).grid(row=i, column=0, padx=10, pady=5, sticky="e")
            entry = tk.Entry(dialog, width=25)
            entry.grid(row=i, column=1, padx=10, pady=5)
            entry.insert(0, value)
            entries[field] = entry
        
        def save():
            code = entries['code'].get()
            name = entries['name'].get()
            category = entries['category'].get()
            unit = entries['unit'].get()
            price = entries['price'].get()
            min_stock = entries['min_stock'].get()
            
            if not code or not name or not unit or not price:
                messagebox.showerror("错误", "请填写必填项")
                return
            
            try:
                price = float(price)
                min_stock = int(min_stock)
            except ValueError:
                messagebox.showerror("错误", "价格和库存必须是数字")
                return
            
            db.update_product(product['id'], code, name, category, unit, price, min_stock)
            messagebox.showinfo("成功", "商品更新成功")
            dialog.destroy()
            self.show_products()
        
        tk.Button(dialog, text="保存", command=save, bg="#3498db", fg="white",
                 font=("微软雅黑", 10), width=10).grid(row=len(fields), column=0, columnspan=2, pady=20)
    
    def show_inbound(self):
        self.clear_content()
        
        # Title
        title_frame = tk.Frame(self.content_frame, bg="white")
        title_frame.pack(fill=tk.X, padx=20, pady=20)
        
        tk.Label(title_frame, text="入库管理", font=("微软雅黑", 16, "bold"),
                bg="white").pack(side=tk.LEFT)
        
        tk.Button(title_frame, text="➕ 新增入库", command=self.add_inbound_dialog,
                 bg="#3498db", fg="white", font=("微软雅黑", 10)).pack(side=tk.RIGHT)
        
        # Treeview
        tree_frame = tk.Frame(self.content_frame, bg="white")
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=20)
        
        columns = ("id", "product", "quantity", "price", "supplier", "user", "time")
        tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)
        
        tree.heading("id", text="编号")
        tree.heading("product", text="商品")
        tree.heading("quantity", text="数量")
        tree.heading("price", text="单价")
        tree.heading("supplier", text="供应商")
        tree.heading("user", text="操作员")
        tree.heading("time", text="时间")
        
        tree.column("id", width=60)
        tree.column("product", width=120)
        tree.column("quantity", width=80)
        tree.column("price", width=80)
        tree.column("supplier", width=120)
        tree.column("user", width=80)
        tree.column("time", width=140)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        records = db.get_inbound_records()
        for r in records:
            tree.insert("", "end", values=(r['id'], r['product_name'], r['quantity'],
                                          f"¥{r['price']:.2f}", r['supplier'] or '-',
                                          r['username'], r['created_at'][:16]))
    
    def add_inbound_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("新增入库")
        dialog.geometry("400x350")
        dialog.resizable(False, False)
        
        products = db.get_all_products()
        
        tk.Label(dialog, text="选择商品:").grid(row=0, column=0, padx=10, pady=10, sticky="e")
        product_combo = ttk.Combobox(dialog, values=[f"{p['code']} - {p['name']}" for p in products],
                                    state="readonly", width=30)
        product_combo.grid(row=0, column=1, padx=10, pady=10)
        
        tk.Label(dialog, text="数量:").grid(row=1, column=0, padx=10, pady=10, sticky="e")
        qty_entry = tk.Entry(dialog, width=33)
        qty_entry.grid(row=1, column=1, padx=10, pady=10)
        
        tk.Label(dialog, text="单价:").grid(row=2, column=0, padx=10, pady=10, sticky="e")
        price_entry = tk.Entry(dialog, width=33)
        price_entry.grid(row=2, column=1, padx=10, pady=10)
        
        tk.Label(dialog, text="供应商:").grid(row=3, column=0, padx=10, pady=10, sticky="e")
        supplier_entry = tk.Entry(dialog, width=33)
        supplier_entry.grid(row=3, column=1, padx=10, pady=10)
        
        tk.Label(dialog, text="备注:").grid(row=4, column=0, padx=10, pady=10, sticky="e")
        note_entry = tk.Entry(dialog, width=33)
        note_entry.grid(row=4, column=1, padx=10, pady=10)
        
        def save():
            if not product_combo.get():
                messagebox.showerror("错误", "请选择商品")
                return
            
            try:
                qty = int(qty_entry.get())
                price = float(price_entry.get())
            except ValueError:
                messagebox.showerror("错误", "数量和价格必须是数字")
                return
            
            idx = product_combo.current()
            product_id = products[idx]['id']
            
            db.add_inbound(product_id, qty, price, supplier_entry.get(), 
                          note_entry.get(), self.user['id'])
            messagebox.showinfo("成功", "入库成功")
            dialog.destroy()
            self.show_inbound()
        
        tk.Button(dialog, text="确认入库", command=save, bg="#3498db", fg="white",
                 font=("微软雅黑", 10), width=12).grid(row=5, column=0, columnspan=2, pady=20)
    
    def show_outbound(self):
        self.clear_content()
        
        # Title
        title_frame = tk.Frame(self.content_frame, bg="white")
        title_frame.pack(fill=tk.X, padx=20, pady=20)
        
        tk.Label(title_frame, text="出库管理", font=("微软雅黑", 16, "bold"),
                bg="white").pack(side=tk.LEFT)
        
        tk.Button(title_frame, text="➕ 新增出库", command=self.add_outbound_dialog,
                 bg="#3498db", fg="white", font=("微软雅黑", 10)).pack(side=tk.RIGHT)
        
        # Treeview
        tree_frame = tk.Frame(self.content_frame, bg="white")
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=20)
        
        columns = ("id", "product", "quantity", "price", "customer", "user", "time")
        tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)
        
        tree.heading("id", text="编号")
        tree.heading("product", text="商品")
        tree.heading("quantity", text="数量")
        tree.heading("price", text="单价")
        tree.heading("customer", text="客户")
        tree.heading("user", text="操作员")
        tree.heading("time", text="时间")
        
        tree.column("id", width=60)
        tree.column("product", width=120)
        tree.column("quantity", width=80)
        tree.column("price", width=80)
        tree.column("customer", width=120)
        tree.column("user", width=80)
        tree.column("time", width=140)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        records = db.get_outbound_records()
        for r in records:
            tree.insert("", "end", values=(r['id'], r['product_name'], r['quantity'],
                                          f"¥{r['price']:.2f}", r['customer'] or '-',
                                          r['username'], r['created_at'][:16]))
    
    def add_outbound_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("新增出库")
        dialog.geometry("400x350")
        dialog.resizable(False, False)
        
        products = db.get_all_products()
        
        tk.Label(dialog, text="选择商品:").grid(row=0, column=0, padx=10, pady=10, sticky="e")
        product_combo = ttk.Combobox(dialog, values=[f"{p['code']} - {p['name']} (库存:{p['stock']})" 
                                                    for p in products],
                                    state="readonly", width=30)
        product_combo.grid(row=0, column=1, padx=10, pady=10)
        
        tk.Label(dialog, text="数量:").grid(row=1, column=0, padx=10, pady=10, sticky="e")
        qty_entry = tk.Entry(dialog, width=33)
        qty_entry.grid(row=1, column=1, padx=10, pady=10)
        
        tk.Label(dialog, text="单价:").grid(row=2, column=0, padx=10, pady=10, sticky="e")
        price_entry = tk.Entry(dialog, width=33)
        price_entry.grid(row=2, column=1, padx=10, pady=10)
        
        tk.Label(dialog, text="客户:").grid(row=3, column=0, padx=10, pady=10, sticky="e")
        customer_entry = tk.Entry(dialog, width=33)
        customer_entry.grid(row=3, column=1, padx=10, pady=10)
        
        tk.Label(dialog, text="备注:").grid(row=4, column=0, padx=10, pady=10, sticky="e")
        note_entry = tk.Entry(dialog, width=33)
        note_entry.grid(row=4, column=1, padx=10, pady=10)
        
        def save():
            if not product_combo.get():
                messagebox.showerror("错误", "请选择商品")
                return
            
            try:
                qty = int(qty_entry.get())
                price = float(price_entry.get())
            except ValueError:
                messagebox.showerror("错误", "数量和价格必须是数字")
                return
            
            idx = product_combo.current()
            product_id = products[idx]['id']
            
            if db.add_outbound(product_id, qty, price, customer_entry.get(), 
                              note_entry.get(), self.user['id']):
                messagebox.showinfo("成功", "出库成功")
                dialog.destroy()
                self.show_outbound()
            else:
                messagebox.showerror("错误", "库存不足")
        
        tk.Button(dialog, text="确认出库", command=save, bg="#3498db", fg="white",
                 font=("微软雅黑", 10), width=12).grid(row=5, column=0, columnspan=2, pady=20)
    
    def show_stock(self):
        self.clear_content()
        
        # Title
        tk.Label(self.content_frame, text="库存查询", font=("微软雅黑", 16, "bold"),
                bg="white").pack(pady=20, anchor="w", padx=20)
        
        # Search frame
        search_frame = tk.Frame(self.content_frame, bg="white")
        search_frame.pack(fill=tk.X, padx=20)
        
        tk.Label(search_frame, text="搜索:", bg="white").pack(side=tk.LEFT)
        search_entry = tk.Entry(search_frame, width=30)
        search_entry.pack(side=tk.LEFT, padx=10)
        
        def search():
            keyword = search_entry.get()
            if keyword:
                products = db.search_products(keyword)
            else:
                products = db.get_all_products()
            refresh_tree(products)
        
        tk.Button(search_frame, text="搜索", command=search, bg="#3498db", fg="white").pack(side=tk.LEFT)
        tk.Button(search_frame, text="刷新", command=lambda: (search_entry.delete(0, tk.END), 
                 refresh_tree(db.get_all_products())), bg="#95a5a6", fg="white").pack(side=tk.LEFT, padx=5)
        
        # Treeview
        tree_frame = tk.Frame(self.content_frame, bg="white")
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        columns = ("code", "name", "category", "unit", "price", "stock", "value", "status")
        tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)
        
        tree.heading("code", text="编码")
        tree.heading("name", text="名称")
        tree.heading("category", text="分类")
        tree.heading("unit", text="单位")
        tree.heading("price", text="单价")
        tree.heading("stock", text="库存")
        tree.heading("value", text="库存金额")
        tree.heading("status", text="状态")
        
        tree.column("code", width=100)
        tree.column("name", width=120)
        tree.column("category", width=80)
        tree.column("unit", width=60)
        tree.column("price", width=80)
        tree.column("stock", width=80)
        tree.column("value", width=100)
        tree.column("status", width=80)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        def refresh_tree(products):
            for item in tree.get_children():
                tree.delete(item)
            for p in products:
                status = "正常"
                tag = ""
                if p['stock'] == 0:
                    status = "缺货"
                    tag = "empty"
                elif p['stock'] <= p['min_stock']:
                    status = "库存不足"
                    tag = "low"
                tree.insert("", "end", values=(p['code'], p['name'], p['category'],
                                              p['unit'], f"¥{p['price']:.2f}", p['stock'],
                                              f"¥{p['price'] * p['stock']:.2f}", status),
                           tags=(tag,))
        
        refresh_tree(db.get_all_products())
        tree.tag_configure("low", foreground="red")
        tree.tag_configure("empty", foreground="gray")
    
    def show_stocktake(self):
        self.clear_content()
        
        # Title
        title_frame = tk.Frame(self.content_frame, bg="white")
        title_frame.pack(fill=tk.X, padx=20, pady=20)
        
        tk.Label(title_frame, text="库存盘点", font=("微软雅黑", 16, "bold"),
                bg="white").pack(side=tk.LEFT)
        
        tk.Button(title_frame, text="➕ 新增盘点", command=self.add_stocktake_dialog,
                 bg="#3498db", fg="white", font=("微软雅黑", 10)).pack(side=tk.RIGHT)
        
        # Treeview
        tree_frame = tk.Frame(self.content_frame, bg="white")
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=20)
        
        columns = ("id", "product", "system", "actual", "diff", "user", "time")
        tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)
        
        tree.heading("id", text="编号")
        tree.heading("product", text="商品")
        tree.heading("system", text="系统库存")
        tree.heading("actual", text="实际库存")
        tree.heading("diff", text="差异")
        tree.heading("user", text="盘点人")
        tree.heading("time", text="时间")
        
        tree.column("id", width=60)
        tree.column("product", width=120)
        tree.column("system", width=80)
        tree.column("actual", width=80)
        tree.column("diff", width=80)
        tree.column("user", width=80)
        tree.column("time", width=140)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        records = db.get_stocktake_records()
        for r in records:
            tag = "plus" if r['difference'] > 0 else ("minus" if r['difference'] < 0 else "")
            tree.insert("", "end", values=(r['id'], r['product_name'], r['system_quantity'],
                                          r['actual_quantity'], r['difference'],
                                          r['username'], r['created_at'][:16]),
                       tags=(tag,))
        
        tree.tag_configure("plus", foreground="green")
        tree.tag_configure("minus", foreground="red")
    
    def add_stocktake_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("新增盘点")
        dialog.geometry("400x280")
        dialog.resizable(False, False)
        
        products = db.get_all_products()
        
        tk.Label(dialog, text="选择商品:").grid(row=0, column=0, padx=10, pady=10, sticky="e")
        product_combo = ttk.Combobox(dialog, values=[f"{p['code']} - {p['name']} (系统:{p['stock']})" 
                                                    for p in products],
                                    state="readonly", width=30)
        product_combo.grid(row=0, column=1, padx=10, pady=10)
        
        tk.Label(dialog, text="实际库存:").grid(row=1, column=0, padx=10, pady=10, sticky="e")
        actual_entry = tk.Entry(dialog, width=33)
        actual_entry.grid(row=1, column=1, padx=10, pady=10)
        
        tk.Label(dialog, text="备注:").grid(row=2, column=0, padx=10, pady=10, sticky="e")
        note_entry = tk.Entry(dialog, width=33)
        note_entry.grid(row=2, column=1, padx=10, pady=10)
        
        def save():
            if not product_combo.get():
                messagebox.showerror("错误", "请选择商品")
                return
            
            try:
                actual = int(actual_entry.get())
            except ValueError:
                messagebox.showerror("错误", "库存必须是整数")
                return
            
            idx = product_combo.current()
            product = products[idx]
            
            db.add_stocktake(product['id'], actual, product['stock'], 
                           note_entry.get(), self.user['id'])
            messagebox.showinfo("成功", "盘点完成")
            dialog.destroy()
            self.show_stocktake()
        
        tk.Button(dialog, text="确认盘点", command=save, bg="#3498db", fg="white",
                 font=("微软雅黑", 10), width=12).grid(row=3, column=0, columnspan=2, pady=20)
    
    def show_returns(self):
        self.clear_content()
        
        # Title
        title_frame = tk.Frame(self.content_frame, bg="white")
        title_frame.pack(fill=tk.X, padx=20, pady=20)
        
        tk.Label(title_frame, text="退入库", font=("微软雅黑", 16, "bold"),
                bg="white").pack(side=tk.LEFT)
        
        tk.Button(title_frame, text="➕ 新增退入库", command=self.add_return_dialog,
                 bg="#3498db", fg="white", font=("微软雅黑", 10)).pack(side=tk.RIGHT)
        
        # Treeview
        tree_frame = tk.Frame(self.content_frame, bg="white")
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=20)
        
        columns = ("id", "product", "quantity", "type", "reason", "user", "time")
        tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)
        
        tree.heading("id", text="编号")
        tree.heading("product", text="商品")
        tree.heading("quantity", text="数量")
        tree.heading("type", text="类型")
        tree.heading("reason", text="原因")
        tree.heading("user", text="操作员")
        tree.heading("time", text="时间")
        
        tree.column("id", width=60)
        tree.column("product", width=120)
        tree.column("quantity", width=80)
        tree.column("type", width=80)
        tree.column("reason", width=150)
        tree.column("user", width=80)
        tree.column("time", width=140)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        records = db.get_return_records()
        for r in records:
            type_text = "退入库" if r['return_type'] == 'inbound' else "退出库"
            tag = "inbound" if r['return_type'] == 'inbound' else "outbound"
            tree.insert("", "end", values=(r['id'], r['product_name'], r['quantity'],
                                          type_text, r['reason'] or '-',
                                          r['username'], r['created_at'][:16]),
                       tags=(tag,))
        
        tree.tag_configure("inbound", foreground="green")
        tree.tag_configure("outbound", foreground="red")
    
    def add_return_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("新增退入库")
        dialog.geometry("400x320")
        dialog.resizable(False, False)
        
        products = db.get_all_products()
        
        tk.Label(dialog, text="选择商品:").grid(row=0, column=0, padx=10, pady=10, sticky="e")
        product_combo = ttk.Combobox(dialog, values=[f"{p['code']} - {p['name']}" for p in products],
                                    state="readonly", width=30)
        product_combo.grid(row=0, column=1, padx=10, pady=10)
        
        tk.Label(dialog, text="数量:").grid(row=1, column=0, padx=10, pady=10, sticky="e")
        qty_entry = tk.Entry(dialog, width=33)
        qty_entry.grid(row=1, column=1, padx=10, pady=10)
        
        tk.Label(dialog, text="类型:").grid(row=2, column=0, padx=10, pady=10, sticky="e")
        type_combo = ttk.Combobox(dialog, values=["退入库 (增加库存)", "退出库 (减少库存)"],
                                 state="readonly", width=30)
        type_combo.grid(row=2, column=1, padx=10, pady=10)
        type_combo.current(0)
        
        tk.Label(dialog, text="原因:").grid(row=3, column=0, padx=10, pady=10, sticky="e")
        reason_entry = tk.Entry(dialog, width=33)
        reason_entry.grid(row=3, column=1, padx=10, pady=10)
        
        def save():
            if not product_combo.get():
                messagebox.showerror("错误", "请选择商品")
                return
            
            try:
                qty = int(qty_entry.get())
            except ValueError:
                messagebox.showerror("错误", "数量必须是整数")
                return
            
            idx = product_combo.current()
            product_id = products[idx]['id']
            return_type = 'inbound' if type_combo.current() == 0 else 'outbound'
            
            db.add_return(product_id, qty, return_type, reason_entry.get(), self.user['id'])
            messagebox.showinfo("成功", "退入库成功")
            dialog.destroy()
            self.show_returns()
        
        tk.Button(dialog, text="确认提交", command=save, bg="#3498db", fg="white",
                 font=("微软雅黑", 10), width=12).grid(row=4, column=0, columnspan=2, pady=20)
    
    def show_reports(self):
        self.clear_content()
        
        # Title
        tk.Label(self.content_frame, text="报表统计", font=("微软雅黑", 16, "bold"),
                bg="white").pack(pady=20, anchor="w", padx=20)
        
        # Date filter
        filter_frame = tk.Frame(self.content_frame, bg="white")
        filter_frame.pack(fill=tk.X, padx=20)
        
        tk.Label(filter_frame, text="开始日期 (YYYY-MM-DD):", bg="white").pack(side=tk.LEFT)
        start_entry = tk.Entry(filter_frame, width=15)
        start_entry.pack(side=tk.LEFT, padx=5)
        start_entry.insert(0, datetime.now().strftime('%Y-%m-01'))
        
        tk.Label(filter_frame, text="结束日期:", bg="white").pack(side=tk.LEFT, padx=(20, 0))
        end_entry = tk.Entry(filter_frame, width=15)
        end_entry.pack(side=tk.LEFT, padx=5)
        end_entry.insert(0, datetime.now().strftime('%Y-%m-%d'))
        
        def query():
            start_date = start_entry.get() + " 00:00:00"
            end_date = end_entry.get() + " 23:59:59"
            inbound, outbound = db.get_report_data(start_date, end_date)
            update_stats(inbound, outbound)
            refresh_inbound(inbound)
            refresh_outbound(outbound)
        
        tk.Button(filter_frame, text="查询", command=query, bg="#3498db", fg="white").pack(side=tk.LEFT, padx=10)
        
        # Stats
        stats_frame = tk.Frame(self.content_frame, bg="white")
        stats_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(stats_frame, text="入库总量:", bg="white", font=("微软雅黑", 10, "bold")).pack(side=tk.LEFT)
        inbound_qty_label = tk.Label(stats_frame, text="0", bg="white", fg="#3498db", font=("微软雅黑", 10))
        inbound_qty_label.pack(side=tk.LEFT, padx=5)
        
        tk.Label(stats_frame, text="出库总量:", bg="white", font=("微软雅黑", 10, "bold")).pack(side=tk.LEFT, padx=(20, 0))
        outbound_qty_label = tk.Label(stats_frame, text="0", bg="white", fg="#e74c3c", font=("微软雅黑", 10))
        outbound_qty_label.pack(side=tk.LEFT, padx=5)
        
        tk.Label(stats_frame, text="入库总值:", bg="white", font=("微软雅黑", 10, "bold")).pack(side=tk.LEFT, padx=(20, 0))
        inbound_val_label = tk.Label(stats_frame, text="¥0", bg="white", fg="#3498db", font=("微软雅黑", 10))
        inbound_val_label.pack(side=tk.LEFT, padx=5)
        
        tk.Label(stats_frame, text="出库总值:", bg="white", font=("微软雅黑", 10, "bold")).pack(side=tk.LEFT, padx=(20, 0))
        outbound_val_label = tk.Label(stats_frame, text="¥0", bg="white", fg="#e74c3c", font=("微软雅黑", 10))
        outbound_val_label.pack(side=tk.LEFT, padx=5)
        
        def update_stats(inbound, outbound):
            in_qty = sum(r['quantity'] for r in inbound)
            out_qty = sum(r['quantity'] for r in outbound)
            in_val = sum(r['quantity'] * r['price'] for r in inbound)
            out_val = sum(r['quantity'] * r['price'] for r in outbound)
            
            inbound_qty_label.config(text=str(in_qty))
            outbound_qty_label.config(text=str(out_qty))
            inbound_val_label.config(text=f"¥{in_val:.2f}")
            outbound_val_label.config(text=f"¥{out_val:.2f}")
        
        # Records frame
        records_frame = tk.Frame(self.content_frame, bg="white")
        records_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Inbound tree
        tk.Label(records_frame, text="入库记录", bg="white", font=("微软雅黑", 10, "bold")).pack(anchor="w")
        
        in_frame = tk.Frame(records_frame, bg="white")
        in_frame.pack(fill=tk.BOTH, expand=True)
        
        in_tree = ttk.Treeview(in_frame, columns=("product", "qty", "price", "time"), 
                              show="headings", height=6)
        in_tree.heading("product", text="商品")
        in_tree.heading("qty", text="数量")
        in_tree.heading("price", text="金额")
        in_tree.heading("time", text="时间")
        in_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Outbound tree
        tk.Label(records_frame, text="出库记录", bg="white", font=("微软雅黑", 10, "bold")).pack(anchor="w", pady=(10, 0))
        
        out_frame = tk.Frame(records_frame, bg="white")
        out_frame.pack(fill=tk.BOTH, expand=True)
        
        out_tree = ttk.Treeview(out_frame, columns=("product", "qty", "price", "time"), 
                               show="headings", height=6)
        out_tree.heading("product", text="商品")
        out_tree.heading("qty", text="数量")
        out_tree.heading("price", text="金额")
        out_tree.heading("time", text="时间")
        out_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        def refresh_inbound(records):
            for item in in_tree.get_children():
                in_tree.delete(item)
            for r in records:
                in_tree.insert("", "end", values=(r['product_name'], r['quantity'],
                                                 f"¥{r['quantity'] * r['price']:.2f}",
                                                 r['created_at'][:16]))
        
        def refresh_outbound(records):
            for item in out_tree.get_children():
                out_tree.delete(item)
            for r in records:
                out_tree.insert("", "end", values=(r['product_name'], r['quantity'],
                                                  f"¥{r['quantity'] * r['price']:.2f}",
                                                  r['created_at'][:16]))
        
        # Initial load
        query()
    
    def show_users(self):
        if self.user['role'] != 'admin':
            messagebox.showerror("错误", "无权限访问")
            return
        
        self.clear_content()
        
        # Title
        title_frame = tk.Frame(self.content_frame, bg="white")
        title_frame.pack(fill=tk.X, padx=20, pady=20)
        
        tk.Label(title_frame, text="用户管理", font=("微软雅黑", 16, "bold"),
                bg="white").pack(side=tk.LEFT)
        
        tk.Button(title_frame, text="➕ 添加用户", command=self.add_user_dialog,
                 bg="#3498db", fg="white", font=("微软雅黑", 10)).pack(side=tk.RIGHT)
        
        # Treeview
        tree_frame = tk.Frame(self.content_frame, bg="white")
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=20)
        
        columns = ("id", "username", "role", "time")
        tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)
        
        tree.heading("id", text="ID")
        tree.heading("username", text="用户名")
        tree.heading("role", text="角色")
        tree.heading("time", text="创建时间")
        
        tree.column("id", width=60)
        tree.column("username", width=150)
        tree.column("role", width=100)
        tree.column("time", width=150)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        users = db.get_all_users()
        for u in users:
            role_text = "管理员" if u['role'] == 'admin' else "普通用户"
            tree.insert("", "end", values=(u['id'], u['username'], role_text, u['created_at'][:16]))
        
        # Delete button
        btn_frame = tk.Frame(self.content_frame, bg="white")
        btn_frame.pack(fill=tk.X, padx=20, pady=10)
        
        def delete_selected():
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("提示", "请选择要删除的用户")
                return
            item = tree.item(selected[0])
            user_id = item['values'][0]
            if item['values'][1] == 'admin':
                messagebox.showerror("错误", "不能删除管理员账户")
                return
            if messagebox.askyesno("确认", "确定要删除此用户吗？"):
                db.delete_user(user_id)
                self.show_users()
        
        tk.Button(btn_frame, text="删除", command=delete_selected, bg="#e74c3c", fg="white",
                 font=("微软雅黑", 10)).pack(side=tk.LEFT)
    
    def add_user_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("添加用户")
        dialog.geometry("350x250")
        dialog.resizable(False, False)
        
        tk.Label(dialog, text="用户名:").grid(row=0, column=0, padx=10, pady=10, sticky="e")
        username_entry = tk.Entry(dialog, width=25)
        username_entry.grid(row=0, column=1, padx=10, pady=10)
        
        tk.Label(dialog, text="密码:").grid(row=1, column=0, padx=10, pady=10, sticky="e")
        password_entry = tk.Entry(dialog, width=25)
        password_entry.grid(row=1, column=1, padx=10, pady=10)
        
        tk.Label(dialog, text="角色:").grid(row=2, column=0, padx=10, pady=10, sticky="e")
        role_combo = ttk.Combobox(dialog, values=["普通用户", "管理员"], state="readonly", width=22)
        role_combo.grid(row=2, column=1, padx=10, pady=10)
        role_combo.current(0)
        
        def save():
            username = username_entry.get()
            password = password_entry.get()
            role = 'admin' if role_combo.current() == 1 else 'user'
            
            if not username or not password:
                messagebox.showerror("错误", "请填写用户名和密码")
                return
            
            if db.add_user(username, password, role):
                messagebox.showinfo("成功", "用户添加成功")
                dialog.destroy()
                self.show_users()
            else:
                messagebox.showerror("错误", "用户名已存在")
        
        tk.Button(dialog, text="保存", command=save, bg="#3498db", fg="white",
                 font=("微软雅黑", 10), width=10).grid(row=3, column=0, columnspan=2, pady=20)
    
    def logout(self):
        self.root.destroy()
        root = tk.Tk()
        LoginWindow(root)
        root.mainloop()

def main():
    db.init_db()
    root = tk.Tk()
    LoginWindow(root)
    root.mainloop()

if __name__ == "__main__":
    main()
