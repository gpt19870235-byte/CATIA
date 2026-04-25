# 刀具管理系統（Tool Management System）

本專案是以 **PostgreSQL + FastAPI + Jinja2 後台頁面** 實作的刀具管理 MVP。

## 功能
- 刀具主檔建立（含壽命分鐘上限、安全庫存）
- 庫存異動：入庫 / 領用 / 歸還 / 報廢
- 使用分鐘累計
- 儀表板警示：低庫存、壽命到期
- API 警示端點

## 快速啟動（Docker）
```bash
docker compose up --build
```

啟動後開啟：
- http://localhost:8000

## 本機啟動
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL='postgresql+psycopg://tool_admin:tool_admin_pw@localhost:5432/tool_management'
uvicorn app.main:app --reload
```

## API
- `GET /api/alerts/low-stock`
- `GET /api/alerts/life-expiring`
