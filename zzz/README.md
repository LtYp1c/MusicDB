# MusicDB - 音乐数据库管理系统

MusicDB 是一个完整的音乐数据库管理系统，提供音乐数据管理和个性化推荐功能。系统采用前后端分离架构，后端使用 Flask + MySQL，前端使用 Vue 3 + Element Plus。

## 🚀 功能特性

### 核心功能
- **用户管理**：用户注册、登录和个人信息管理
- **歌手管理**：歌手信息维护和展示
- **专辑管理**：专辑信息与歌曲关联
- **歌曲管理**：完整的歌曲信息管理
- **收藏功能**：用户收藏喜欢的歌曲
- **播放列表**：创建和管理个人播放列表
- **音乐流派**：歌曲流派分类管理

### 推荐系统
- **个性化推荐**：基于用户收藏行为的智能推荐
- **热门推荐**：最新歌曲和热门歌手展示
- **收藏统计**：显示歌曲和歌手的收藏次数

### 数据统计
- 系统概览统计（用户、歌手、专辑、歌曲数量）
- 热门歌手排行榜
- 最新歌曲展示

## 🛠️ 技术栈

### 后端技术
- **框架**：Flask 2.3.3
- **数据库**：MySQL + SQLAlchemy ORM
- **认证**：基于用户ID的简单认证
- **跨域**：Flask-CORS
- **环境配置**：python-dotenv

### 前端技术
- **框架**：Vue 3.3.4 + Vue Router 4.2.4
- **UI组件**：Element Plus 2.3.8
- **构建工具**：Vite 4.4.5
- **HTTP客户端**：Axios 1.4.0

## 📦 项目结构

```
MusicDB/
├── app.py                 # Flask应用入口
├── models.py             # 数据库模型定义
├── routes.py             # API路由定义
├── init_db.py            # 数据库初始化脚本
├── requirements.txt      # Python依赖
├── .env                  # 环境配置文件
├── frontend/             # 前端项目
│   ├── src/
│   │   ├── views/        # 页面组件
│   │   ├── api/          # API接口封装
│   │   ├── router/        # 路由配置
│   │   └── utils/         # 工具函数
│   ├── package.json       # 前端依赖
│   └── vite.config.js     # Vite配置
└── README.md             # 项目说明
```

## 🚀 快速开始

### 环境要求
- Python 3.8+
- Node.js 14+
- MySQL 5.7+

### 后端部署

1. **克隆项目**
```bash
git clone <repository-url>
cd MusicDB
```

2. **创建虚拟环境**
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate
```

3. **安装依赖**
```bash
pip install -r requirements.txt
```

4. **配置数据库**
创建 `.env` 文件并配置数据库连接：
```env
DB_HOST=localhost
DB_PORT=3306
DB_USERNAME=root
DB_PASSWORD=your_password
DB_NAME=musicdb
```

5. **初始化数据库**
```bash
python init_db.py
```

6. **启动后端服务**
```bash
python app.py
```
后端服务将在 http://localhost:5000 启动

### 前端部署

1. **进入前端目录**
```bash
cd frontend
```

2. **安装依赖**
```bash
npm install
```

3. **启动开发服务器**
```bash
npm run dev
```
前端服务将在 http://localhost:5173 启动

## 📊 数据库设计

### 核心数据表

- **users**：用户信息表
- **singers**：歌手信息表
- **albums**：专辑信息表
- **songs**：歌曲信息表
- **favorites**：用户收藏表
- **playlists**：播放列表表
- **genres**：音乐流派表
- **song_genres**：歌曲流派关联表

### 关系说明
- 歌手与专辑：一对多关系
- 专辑与歌曲：一对多关系
- 用户与收藏：一对多关系
- 歌曲与流派：多对多关系

## 🔌 API接口

### 用户相关
- `GET /api/users` - 获取用户列表
- `POST /api/users` - 创建新用户
- `GET /api/users/<id>` - 获取用户详情

### 歌手相关
- `GET /api/singers` - 获取歌手列表
- `POST /api/singers` - 创建新歌手
- `GET /api/singers/<id>` - 获取歌手详情

### 歌曲相关
- `GET /api/songs` - 获取歌曲列表
- `POST /api/songs` - 创建新歌曲
- `GET /api/songs/<id>` - 获取歌曲详情

### 收藏相关
- `GET /api/favorites` - 获取收藏列表
- `POST /api/favorites` - 添加收藏
- `DELETE /api/favorites/<id>` - 取消收藏

### 推荐相关
- `GET /api/recommendations?user_id=<id>` - 获取个人推荐
- `GET /api/recommendations/popular` - 获取热门推荐

## 🎯 推荐算法

### 个性化推荐机制
1. **基于用户收藏**：分析用户收藏的歌曲和歌手
2. **歌手相似度**：推荐用户收藏歌手的其他歌曲
3. **最新补充**：推荐数量不足时补充最新歌曲
4. **去重处理**：排除用户已收藏的歌曲

### 热门推荐
- 返回最新添加的10首歌曲
- 按创建时间倒序排列

## 🎨 前端界面

### 主要页面
- **仪表盘**：系统概览、最新歌曲、热门歌手、个人推荐
- **用户管理**：用户信息管理
- **歌手管理**：歌手信息维护
- **歌曲管理**：歌曲信息管理
- **播放列表**：播放列表创建和管理

### UI特性
- 响应式设计，支持移动端
- Element Plus组件库
- 现代化的卡片布局
- 实时数据统计展示

## 🔧 开发指南

### 添加新的API接口
1. 在 `routes.py` 中添加新的路由函数
2. 在 `models.py` 中定义相关数据模型（如果需要）
3. 在前端 `api` 目录中添加对应的API调用函数
4. 在前端页面中使用新的API

### 数据库迁移
当修改数据模型时：
1. 更新 `models.py` 中的模型定义
2. 删除现有数据库表
3. 重新运行 `init_db.py` 初始化数据库

### 前端开发
- 使用 `npm run dev` 启动开发服务器
- 支持热重载，修改代码自动刷新
- 使用 Vue 3 Composition API

## 🐛 故障排除

### 常见问题

1. **数据库连接失败**
   - 检查MySQL服务是否启动
   - 确认 `.env` 文件中的数据库配置正确

2. **端口冲突**
   - 后端默认端口：5000
   - 前端默认端口：5173
   - 修改端口可在配置文件中调整

3. **依赖安装失败**
   - 确保使用正确的Python和Node.js版本
   - 清除缓存后重新安装依赖

## 🤝 贡献指南

1. Fork 本项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 👥 开发团队

- 项目维护者：MusicDB Team
- 联系方式：example@email.com

## 🔮 未来规划

- [ ] 用户认证系统增强
- [ ] 音乐文件上传和播放功能
- [ ] 更复杂的推荐算法
- [ ] 移动端App开发
- [ ] 第三方音乐平台集成

---

**MusicDB** - 让音乐管理更简单！ 🎵