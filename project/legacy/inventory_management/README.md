# 出入库管理系统

一个基于Flask和SQLite的出入库管理系统，提供Web界面进行商品管理、出入库操作、库存查询、盘点、退入库和报表统计。

## 功能特性

- 用户认证与权限管理
- 商品信息管理（增删改查）
- 入库管理
- 出库管理
- 库存查询与搜索
- 库存盘点
- 退入库管理
- 报表统计
- 库存预警

## 技术栈

- 后端：Python Flask
- 数据库：SQLite
- 前端：Bootstrap 5 + HTML/CSS/JavaScript

## 安装与运行

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 运行应用

```bash
python run.py
```

### 3. 访问应用

打开浏览器访问：http://localhost:5000

### 默认账户

- 用户名：admin
- 密码：admin123

## 项目结构

```
inventory_management/
├── app/
│   ├── __init__.py      # Flask应用初始化
│   ├── models.py        # 数据库模型
│   ├── routes.py        # 路由处理
│   └── templates/       # HTML模板
│       ├── base.html
│       ├── login.html
│       ├── dashboard.html
│       ├── products.html
│       ├── inbound.html
│       ├── outbound.html
│       ├── stock.html
│       ├── stocktake.html
│       ├── returns.html
│       ├── reports.html
│       └── users.html
├── static/
│   └── css/
│       └── style.css    # 自定义样式
├── requirements.txt     # Python依赖
└── run.py              # 应用入口
```

## 使用说明

1. **登录系统**：使用默认管理员账户登录
2. **商品管理**：添加、编辑、删除商品信息
3. **入库操作**：记录商品入库信息，自动更新库存
4. **出库操作**：记录商品出库信息，自动更新库存
5. **库存查询**：按编码、名称、分类搜索商品
6. **库存盘点**：定期盘点，调整系统库存
7. **退入库**：处理退货或退库业务
8. **报表统计**：查看指定时间段的出入库统计
9. **用户管理**：管理员可添加、删除用户

## 注意事项

- 生产环境请修改`SECRET_KEY`
- 建议定期备份数据库文件`inventory.db`
- 可根据需要修改最低库存预警阈值
