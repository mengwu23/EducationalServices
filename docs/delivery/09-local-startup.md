# 09 本地启动规划

本文件描述未来开发阶段的本地启动方式。当前阶段只写文档，不创建启动脚本和代码目录。

## 启动方式

项目采用本地脚本启动，不使用 Docker Compose 或 Kubernetes。

规划脚本：

- `backend/start_backend.ps1`
- `frontend/start_frontend.ps1`
- `scripts/start_all.ps1`
- `scripts/init_mysql.sql`

## 后端启动规划

后端启动前需要：

1. 安装 Python 依赖。
2. 配置 `.env`。
3. 初始化 MySQL 数据库。
4. 执行 Alembic 迁移。
5. 启动 FastAPI 服务。

建议命令：

```powershell
cd backend
python -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

## 前端启动规划

前端启动前需要：

1. 安装 Node.js 依赖。
2. 配置 `.env`。
3. 启动 Vue 开发服务。

建议命令：

```powershell
cd frontend
npm install
npm run dev
```

## 环境变量规划

后端 `.env.example` 应包含：

```text
APP_ENV=local
DATABASE_URL=mysql+pymysql://user:password@127.0.0.1:3306/education_service
DIFY_API_BASE_URL=http://127.0.0.1:5001
DIFY_API_KEY=replace_with_local_key
JWT_SECRET_KEY=replace_with_local_secret
```

前端 `.env.example` 应包含：

```text
VITE_API_BASE_URL=http://127.0.0.1:8000/api/v1
```

## 本地联调检查

- 后端健康检查接口可访问。
- 前端能访问登录页。
- 前端接口地址指向本地后端。
- 后端能连接 MySQL。
- 后端能调用 Dify 测试接口。
- 草稿确认接口能创建和查询测试草稿。
