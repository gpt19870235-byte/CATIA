from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, Enum as SQLEnum, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class TransactionType(str, Enum):
    IN = "IN"
    OUT = "OUT"
    RETURN = "RETURN"
    SCRAP = "SCRAP"


class Tool(Base):
    __tablename__ = "tools"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(200))
    model: Mapped[str] = mapped_column(String(120))
    vendor: Mapped[str] = mapped_column(String(120))
    applicable_machine: Mapped[str] = mapped_column(String(120))
    life_minutes_limit: Mapped[int] = mapped_column(Integer)
    safety_stock: Mapped[int] = mapped_column(Integer, default=0)
    current_stock: Mapped[int] = mapped_column(Integer, default=0)
    used_minutes_total: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    transactions: Mapped[list["ToolTransaction"]] = relationship(back_populates="tool")
    usage_logs: Mapped[list["ToolUsageLog"]] = relationship(back_populates="tool")


class ToolTransaction(Base):
    __tablename__ = "tool_transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    tool_id: Mapped[int] = mapped_column(ForeignKey("tools.id"), index=True)
    transaction_type: Mapped[TransactionType] = mapped_column(SQLEnum(TransactionType))
    quantity: Mapped[int] = mapped_column(Integer)
    operator_name: Mapped[str] = mapped_column(String(120), default="system")
    work_order: Mapped[str] = mapped_column(String(120), default="N/A")
    machine_name: Mapped[str] = mapped_column(String(120), default="N/A")
    note: Mapped[str] = mapped_column(String(255), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    tool: Mapped[Tool] = relationship(back_populates="transactions")


class ToolUsageLog(Base):
    __tablename__ = "tool_usage_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    tool_id: Mapped[int] = mapped_column(ForeignKey("tools.id"), index=True)
    minutes_used: Mapped[int] = mapped_column(Integer)
    work_order: Mapped[str] = mapped_column(String(120), default="N/A")
    machine_name: Mapped[str] = mapped_column(String(120), default="N/A")
    efficiency_factor: Mapped[float] = mapped_column(Float, default=1.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    tool: Mapped[Tool] = relationship(back_populates="usage_logs")
