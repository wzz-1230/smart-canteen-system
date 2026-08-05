# 智慧食堂管理系统

## 1. 项目介绍
智慧食堂管理系统是一套面向高校及企事业单位食堂的综合性数字化运营管理平台，旨在解决传统食堂管理模式中菜单维护效率低下、订单流转不透明、运营数据缺乏支撑、用户反馈响应滞后等痛点。

系统采用前后端分离架构，后端基于 FastAPI 异步框架与 SQLAlchemy ORM，前端基于 Vue 3 + Element Plus 技术栈，结合 ECharts 与 AntV G2Plot 实现数据可视化，集成大语言模型提供智能问答服务，支持 MySQL、PostgreSQL、SQLite 多数据库适配。

系统核心由七大模块构成：

首页驾驶舱：集中呈现菜品统计、订单概览、用户活跃度及服务器运行状态等关键指标，辅助管理者快速掌握全局运营情况。
食堂管理：提供菜品信息维护、多级分类管理、图片上传、营养成分标注、库存预警及批量导入导出等完整能力，为日常运营奠定数据基础。
线上点单：覆盖购物车管理、在线下单、订单状态跟踪（待支付→制作中→已完成）及历史订单查询的全流程闭环。
食堂智能助手：基于大语言模型提供菜品推荐、营养咨询、常见问题解答等智能化服务，支持多轮对话与流式输出。
数据可视化：从销售趋势、菜品热度、用户消费画像、营养成分等多维度展开分析，为运营决策提供数据支撑。
系统管理：基于 RBAC 模型实现用户、角色、菜单、部门、岗位、字典、参数及日志的细粒度管理，支持菜单级与按钮级权限控制。
系统监控：实时展示服务器 CPU、内存、磁盘指标，提供 Redis 缓存管理、在线用户追踪及定时任务调度等运维能力。
通过以上模块的协同运作，系统打通了菜品维护、订单处理、智能问答、数据分析与系统运维等关键环节，形成数据共享、业务协同、分析智能、决策支持一体化的综合管理体系，有效提升食堂运营效率与服务质量。
### 1.1 项目解决什么问题

随着高校后勤信息化建设的不断深入，传统食堂管理模式面临着诸多挑战：菜单管理效率低下、食材消耗难以统计、用户反馈响应滞后、运营决策缺乏数据支撑等问题日益突出。

**智慧食堂管理系统**基于现代化的前后端分离技术架构，通过集成菜品管理、订单处理、库存监控、数据分析与可视化展示、AI 智能助手等核心功能模块，为食堂运营管理提供全方位的数字化解决方案。

### 1.2 技术架构

- **前端技术栈**：Vue 3（Composition API）+ Element Plus + ECharts + AntV G2Plot + Pinia + Vite
- **后端技术栈**：FastAPI + SQLAlchemy（Async）+ Redis + PyJWT + Loguru
- **数据库支持**：MySQL / PostgreSQL / SQLite
- **部署架构**：前后端分离，支持 Nginx 反向代理

## 2. 主要功能

### 2.1 首页驾驶舱
- 系统访问量统计（今日访问量、总访问量、在线用户数）
- 食堂菜品状态统计（菜品总数、上架菜品数、下架菜品数）
- 订单处理情况（今日订单数、待处理订单、已完成订单）
- 系统运行状态监控（CPU、内存、磁盘使用率）
- 用户活跃度趋势图表
- 快捷操作入口

### 2.2 食堂管理模块
- **菜品管理**：菜品新增、编辑、删除、查询，支持按名称、分类、状态筛选
- **分类管理**：多级分类树结构，支持层级管理
- **图片管理**：菜品图片上传与展示，支持本地存储与 AI 生成图片
- **营养信息**：热量、蛋白质、脂肪、碳水化合物等营养成分维护
- **库存管理**：库存数量登记、库存预警、出入库记录
- **批量操作**：菜品批量导入（Excel/CSV）、批量导出、批量上下架

### 2.3 线上点单模块
- **购物车管理**：菜品加入购物车、数量调整、删除、清空
- **订单创建**：选择菜品、填写备注、提交订单
- **订单跟踪**：订单状态实时更新（待支付、制作中、已完成、已取消）
- **历史订单**：订单搜索筛选、历史订单回看、订单导出
- **订单分析**：按时间、菜品、用户维度统计分析

### 2.4 食堂智能助手
- **智能问答**：基于大语言模型的问答服务（支持 OpenAI、Anthropic、Ollama 等多个提供商）
- **菜品推荐**：根据用户偏好、菜品热度、营养需求进行个性化推荐
- **对话管理**：对话历史记录、上下文管理、多轮对话支持
- **知识库管理**：菜品知识、营养知识、常见问题解答库维护

### 2.5 数据可视化模块
- **销售分析**：按日/周/月/年维度展示销售额、订单量、客单价趋势
- **菜品热度排行**：菜品销量排行、热门菜品 TOP10
- **用户消费画像**：消费频次、消费时段、偏好菜品分析
- **营养分析**：营养成分汇总统计与多维分析
- **综合驾驶舱**：关键指标一站式展示

### 2.6 系统管理模块
- **用户管理**：用户 CRUD、角色分配、密码重置、状态切换
- **角色管理**：角色权限分配、数据权限设置
- **菜单管理**：菜单树维护、按钮级权限配置
- **部门管理**：组织架构树管理
- **岗位管理**：岗位信息维护
- **字典管理**：字典类型与字典数据维护
- **参数配置**：系统运行参数管理（验证码开关、分页大小等）
- **日志管理**：操作日志、登录日志查询与导出

### 2.7 系统监控模块
- **服务器监控**：CPU、内存、磁盘使用率实时展示
- **缓存管理**：Redis 缓存浏览、查询、删除
- **在线用户**：在线用户列表、强制下线
- **定时任务**：任务配置、执行日志查看
- **JWT 令牌管理**：活跃 Token 列表、强制失效

## 3. 安装方法

### 3.1 环境要求

| 软件 | 版本要求 | 说明 |
|-----|---------|------|
| Python | 3.9+ | 推荐 3.10 或 3.11 |
| Node.js | 16+ | 推荐 18 LTS |
| MySQL | 5.7+ | 推荐 8.0（可选 PostgreSQL 或 SQLite） |
| Redis | 5.0+ | 推荐 6.x 或 7.x |

### 3.2 后端安装与启动

```bash
# 1. 进入后端目录
cd 项目源代码/后端目录

# 2. 创建并激活虚拟环境
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt
# 国内镜像源（可选）：
# pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 4. 修改配置文件 .env.dev（默认配置如下）
# 数据库配置
DB_TYPE=mysql
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USERNAME=root
DB_PASSWORD=your_password
DB_DATABASE=ruoyi-fastapi

# Redis 配置
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DATABASE=2

# 5. 启动后端服务
python app.py
# 或使用 uvicorn：
# uvicorn app:app --host 0.0.0.0 --port 9099 --reload

# 6. 验证启动
# 访问 http://127.0.0.1:9099/docs 查看 Swagger API 文档
```

### 3.3 前端安装与启动

```bash
# 1. 进入前端目录
cd 项目源代码/前端目录

# 2. 安装依赖
npm install
# 国内镜像源（可选）：
# npm config set registry https://registry.npmmirror.com
# npm install

# 3. 修改配置文件（如需）
# 前端默认配置：
# VITE_APP_BASE_API = '/dev-api'
# 后端代理：/dev-api → http://127.0.0.1:9099

# 4. 启动前端开发服务器
npm run dev

# 5. 访问系统
# 浏览器打开 http://localhost:8080
```

### 3.4 生产环境部署

```bash
# 前端构建
cd 项目源代码/前端目录
npm run build:prod
# 构建产物在 dist/ 目录

# 后端部署（使用 uvicorn 多进程）
cd 项目源代码/后端目录
uvicorn app:app --host 0.0.0.0 --port 9099 --workers 4
```

### 3.5 默认账号

系统首次启动后，默认管理员账号：
- **用户名**：`admin`
- **密码**：`admin123`

> ⚠️ 首次登录后请立即修改默认密码！

## 4. 使用方法

### 4.1 登录系统

1. 浏览器访问系统地址（开发环境：`http://localhost:8080`）
2. 自动跳转至登录页面
3. 输入用户名 `admin` 和密码 `admin123`
4. 点击"登录"按钮，登录成功后自动进入首页驾驶舱

### 4.2 菜品管理

1. 进入 **食堂管理 → 菜品管理**
2. 点击 **+ 新增** 按钮
3. 填写菜品信息：名称、分类、价格、描述、营养成分
4. 上传菜品图片（支持 jpg/png/webp/gif 格式）
5. 点击"确定"保存

### 4.3 线上点单

1. 进入 **线上点单** 页面
2. 浏览菜品卡片，按分类或搜索筛选
3. 点击 **+** 将菜品加入购物车
4. 查看购物车，调整数量或删除菜品
5. 填写订单备注，点击 **提交订单**
6. 在 **我的订单** 中查看订单状态和历史

### 4.4 使用智能助手

1. 进入 **食堂智能助手**
2. 在输入框中输入问题，例如：
   - "今天有什么推荐的菜品？"
   - "哪些菜品是低热量的？"
   - "红烧肉的营养成分有哪些？"
3. 系统流式展示 AI 回答，支持 Markdown 格式
4. 支持多轮对话，系统自动维护上下文

### 4.5 数据可视化

1. 进入 **数据可视化** 模块
2. 查看综合驾驶舱：今日销售额、本月销售额、订单总数
3. 切换子页面查看详细分析：
   - 销售分析：趋势折线图
   - 菜品分析：销量排行柱状图
   - 用户画像：消费时段分布饼图
4. 支持时间范围筛选（今日/本周/本月/本年）

## 5. 输入输出示例

### 5.1 登录接口

**请求**：
```
POST /dev-api/login
Content-Type: application/json

{
  "username": "admin",
  "password": "admin123",
  "code": "验证码内容",
  "uuid": "验证码UUID"
}
```

**响应**：
```json
{
  "code": 200,
  "msg": "操作成功",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}
```

### 5.2 获取菜品列表

**请求**：
```
GET /dev-api/canteen/menu-list?page_num=1&page_size=10&menu_name=红&status=1
Authorization: Bearer {token}
```

**响应**：
```json
{
  "code": 200,
  "msg": "操作成功",
  "data": {
    "total": 150,
    "rows": [
      {
        "id": 1,
        "menu_name": "红烧肉",
        "menu_price": 18.00,
        "menu_type": "荤菜",
        "status": 1,
        "menu_image": "/profile/upload/2026/06/25/hongshaorou.jpg",
        "calories": 395,
        "protein": 7.5,
        "fat": 26.0,
        "carbs": 1.2
      }
    ]
  }
}
```

### 5.3 创建订单

**请求**：
```
POST /dev-api/canteen/order
Authorization: Bearer {token}

{
  "remark": "不要香菜",
  "items": [
    {
      "menu_id": 1,
      "quantity": 2
    },
    {
      "menu_id": 5,
      "quantity": 1
    }
  ]
}
```

**响应**：
```json
{
  "code": 200,
  "msg": "下单成功",
  "data": {
    "order_id": 1001,
    "order_no": "ORD20260805001",
    "total_amount": 42.00,
    "status": "pending"
  }
}
```

### 5.4 智能助手对话

**请求**：
```
POST /dev-api/ai/chat
Authorization: Bearer {token}

{
  "message": "今天有什么推荐的菜品？",
  "conversation_id": "可选，多轮对话时传入"
}
```

**响应**（流式）：
```json
{
  "code": 200,
  "msg": "操作成功",
  "data": {
    "conversation_id": "conv_abc123",
    "reply": "根据今日供应和菜品热度，为您推荐以下菜品：\n\n1. **红烧肉** ⭐ 月售 328 份\n   - 价格：¥18\n   - 特点：肥而不腻，入口即化\n   - 热量：395 kcal\n\n2. **宫保鸡丁** ⭐ 月售 256 份\n   - 价格：¥16\n   - 特点：酸甜微辣，经典川菜\n   - 热量：280 kcal\n\n3. **番茄炒蛋** ⭐ 月售 198 份\n   - 价格：¥12\n   - 特点：营养健康，老少皆宜\n   - 热量：220 kcal\n\n> 💡 以上数据基于近 30 天销售统计"
  }
}
```

### 5.5 数据可视化接口

**请求**：
```
GET /dev-api/visualization/dashboard?date_range=30d
Authorization: Bearer {token}
```

**响应**：
```json
{
  "code": 200,
  "msg": "操作成功",
  "data": {
    "overview": {
      "today_sales": 1280.50,
      "today_orders": 56,
      "active_users": 128,
      "total_menus": 150,
      "online_menus": 120
    },
    "sales_trend": [
      { "date": "2026-07-07", "sales": 1150, "orders": 48 },
      { "date": "2026-07-08", "sales": 1320, "orders": 55 },
      { "date": "2026-07-09", "sales": 1080, "orders": 42 }
    ],
    "top_menus": [
      { "name": "红烧肉", "count": 328, "amount": 5904 },
      { "name": "宫保鸡丁", "count": 256, "amount": 4096 },
      { "name": "番茄炒蛋", "count": 198, "amount": 2376 }
    ],
    "user_profile": {
      "time_distribution": [
        { "period": "早餐", "percentage": 25 },
        { "period": "午餐", "percentage": 55 },
        { "period": "晚餐", "percentage": 20 }
      ],
      "preference": [
        { "type": "荤菜", "percentage": 45 },
        { "type": "素菜", "percentage": 35 },
        { "type": "汤品", "percentage": 20 }
      ]
    }
  }
}
```

## 6. 目录结构

```
233011050103-韦浈浈-智慧食堂管理系统/
├── README.md                          # 项目说明文档
├── .gitignore                         # Git 忽略规则
└── 项目源代码/
    ├── 前端目录/                      # 前端项目
    │   ├── src/
    │   │   ├── api/                   # API 接口定义
    │   │   │   ├── ai/                # AI 相关接口
    │   │   │   ├── canteen/           # 食堂管理接口
    │   │   │   ├── monitor/           # 系统监控接口
    │   │   │   ├── system/            # 系统管理接口
    │   │   │   └── ...
    │   │   ├── assets/                # 静态资源
    │   │   ├── components/            # 公共组件
    │   │   ├── layout/                # 布局组件
    │   │   ├── router/                # 路由配置
    │   │   ├── store/                 # 状态管理
    │   │   ├── utils/                 # 工具函数
    │   │   └── views/                 # 页面视图
    │   │       ├── canteen/           # 食堂管理页面
    │   │       ├── monitor/           # 系统监控页面
    │   │       ├── system/            # 系统管理页面
    │   │       ├── visualization/     # 数据可视化页面
    │   │       └── ...
    │   ├── index.html                 # 入口 HTML
    │   ├── package.json               # 依赖配置
    │   └── vite.config.js             # Vite 配置
    │
    └── 后端目录/                      # 后端项目
        ├── config/                    # 配置文件
        │   └── env.py                 # 环境配置
        ├── module_admin/              # 系统管理模块
        │   ├── controller/            # 控制器
        │   ├── service/               # 业务逻辑
        │   ├── dao/                   # 数据访问
        │   └── entity/                # 数据模型
        ├── module_ai/                 # AI 模块
        ├── module_generator/          # 代码生成器
        ├── cli/                       # CLI 命令行工具
        ├── common/                    # 公共模块
        ├── middlewares/               # 中间件
        ├── sql/                       # SQL 初始化脚本
        ├── static/                    # 静态资源（菜品图片）
        ├── app.py                     # 启动入口
        ├── server.py                  # 应用工厂
        ├── requirements.txt           # Python 依赖
        └── pyproject.toml            # 项目配置
```

## 7. 常见问题

### Q1：启动后无法登录？
检查以下内容：
- 后端服务是否正常启动（端口 9099）
- `.env.dev` 数据库和 Redis 配置是否正确
- MySQL 和 Redis 服务是否正常运行
- 前端 API 地址配置是否正确

### Q2：数据库表未自动创建？
- 确认数据库 `ruoyi-fastapi` 已创建
- 确认数据库用户名密码正确
- 查看启动日志是否有报错

### Q3：验证码不显示？
- 确认 Redis 服务已启动
- 检查 `.env.dev` Redis 配置
- 可在"系统管理-参数设置"关闭验证码

### Q4：菜单或按钮不显示？
- 确认当前用户已分配角色
- 检查角色的菜单权限配置
- 权限变更后需重新登录

### Q5：图片上传失败？
- 检查图片格式（jpg/jpeg/png/webp/gif）
- 检查图片大小（默认最大 10MB）
- 检查后端上传目录写入权限

## 8. 技术特色

- **前后端分离架构**：FastAPI + Vue 3，性能优越，体验流畅
- **AI 智能助手**：集成大语言模型，支持多提供商（OpenAI、Anthropic、Ollama 等）
- **数据可视化**：ECharts + AntV G2Plot，丰富的图表展示
- **异步处理**：全链路异步编程，高并发性能
- **多数据库支持**：MySQL / PostgreSQL / SQLite
- **权限管理**：RBAC 细粒度权限控制，支持菜单级、按钮级、数据级权限
- **代码生成器**：可视化代码生成，快速开发新模块
