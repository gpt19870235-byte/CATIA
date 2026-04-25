from fastapi import Depends, FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from .models import Tool, ToolTransaction, ToolUsageLog, TransactionType

app = FastAPI(title="刀具管理系統")
templates = Jinja2Templates(directory="templates")

Base.metadata.create_all(bind=engine)


@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)):
    tools = db.scalars(select(Tool).order_by(Tool.id.desc())).all()
    total_tools = len(tools)
    low_stock_count = len([t for t in tools if t.current_stock <= t.safety_stock])
    life_alert_count = len([t for t in tools if t.used_minutes_total >= t.life_minutes_limit])

    recent_txn = db.scalars(
        select(ToolTransaction).order_by(ToolTransaction.created_at.desc()).limit(10)
    ).all()

    return templates.TemplateResponse(
        request,
        "dashboard.html",
        {
            "tools": tools,
            "total_tools": total_tools,
            "low_stock_count": low_stock_count,
            "life_alert_count": life_alert_count,
            "recent_txn": recent_txn,
        },
    )


@app.get("/tools/new", response_class=HTMLResponse)
def new_tool_form(request: Request):
    return templates.TemplateResponse(request, "tool_new.html", {})


@app.post("/tools")
def create_tool(
    code: str = Form(...),
    name: str = Form(...),
    model: str = Form(...),
    vendor: str = Form(...),
    applicable_machine: str = Form(...),
    life_minutes_limit: int = Form(...),
    safety_stock: int = Form(...),
    db: Session = Depends(get_db),
):
    exists = db.scalar(select(Tool).where(Tool.code == code))
    if exists:
        raise HTTPException(status_code=400, detail="刀具編號已存在")

    tool = Tool(
        code=code,
        name=name,
        model=model,
        vendor=vendor,
        applicable_machine=applicable_machine,
        life_minutes_limit=life_minutes_limit,
        safety_stock=safety_stock,
        current_stock=0,
    )
    db.add(tool)
    db.commit()
    return RedirectResponse(url="/", status_code=303)


@app.get("/transactions/new", response_class=HTMLResponse)
def new_transaction_form(request: Request, db: Session = Depends(get_db)):
    tools = db.scalars(select(Tool).order_by(Tool.code.asc())).all()
    return templates.TemplateResponse(request, "transaction_new.html", {"tools": tools})


@app.post("/transactions")
def create_transaction(
    tool_id: int = Form(...),
    transaction_type: TransactionType = Form(...),
    quantity: int = Form(...),
    operator_name: str = Form("system"),
    work_order: str = Form("N/A"),
    machine_name: str = Form("N/A"),
    note: str = Form(""),
    db: Session = Depends(get_db),
):
    tool = db.get(Tool, tool_id)
    if not tool:
        raise HTTPException(status_code=404, detail="找不到刀具")

    if quantity <= 0:
        raise HTTPException(status_code=400, detail="數量必須大於 0")

    stock_delta = 0
    if transaction_type == TransactionType.IN or transaction_type == TransactionType.RETURN:
        stock_delta = quantity
    elif transaction_type == TransactionType.OUT or transaction_type == TransactionType.SCRAP:
        stock_delta = -quantity

    if tool.current_stock + stock_delta < 0:
        raise HTTPException(status_code=400, detail="庫存不足")

    tool.current_stock += stock_delta

    txn = ToolTransaction(
        tool_id=tool_id,
        transaction_type=transaction_type,
        quantity=quantity,
        operator_name=operator_name,
        work_order=work_order,
        machine_name=machine_name,
        note=note,
    )
    db.add(txn)
    db.commit()
    return RedirectResponse(url="/", status_code=303)


@app.get("/usage/new", response_class=HTMLResponse)
def new_usage_form(request: Request, db: Session = Depends(get_db)):
    tools = db.scalars(select(Tool).order_by(Tool.code.asc())).all()
    return templates.TemplateResponse(request, "usage_new.html", {"tools": tools})


@app.post("/usage")
def create_usage(
    tool_id: int = Form(...),
    minutes_used: int = Form(...),
    work_order: str = Form("N/A"),
    machine_name: str = Form("N/A"),
    db: Session = Depends(get_db),
):
    tool = db.get(Tool, tool_id)
    if not tool:
        raise HTTPException(status_code=404, detail="找不到刀具")
    if minutes_used <= 0:
        raise HTTPException(status_code=400, detail="使用分鐘數必須大於 0")

    tool.used_minutes_total += minutes_used
    log = ToolUsageLog(
        tool_id=tool_id,
        minutes_used=minutes_used,
        work_order=work_order,
        machine_name=machine_name,
    )

    db.add(log)
    db.commit()
    return RedirectResponse(url="/", status_code=303)


@app.get("/api/alerts/low-stock")
def low_stock_alerts(db: Session = Depends(get_db)):
    tools = db.scalars(select(Tool)).all()
    alerts = [
        {
            "tool_code": tool.code,
            "tool_name": tool.name,
            "current_stock": tool.current_stock,
            "safety_stock": tool.safety_stock,
        }
        for tool in tools
        if tool.current_stock <= tool.safety_stock
    ]
    return {"alerts": alerts}


@app.get("/api/alerts/life-expiring")
def life_expiring_alerts(db: Session = Depends(get_db)):
    tools = db.scalars(select(Tool)).all()
    alerts = [
        {
            "tool_code": tool.code,
            "tool_name": tool.name,
            "used_minutes_total": tool.used_minutes_total,
            "life_minutes_limit": tool.life_minutes_limit,
        }
        for tool in tools
        if tool.used_minutes_total >= tool.life_minutes_limit
    ]
    return {"alerts": alerts}
