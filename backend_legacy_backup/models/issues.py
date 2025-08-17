"""
Issue models
نماذج المشاكل
"""

from sqlalchemy import Column, Integer, String, ForeignKey, Text, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database.config import Base


class Issue(Base):
    """Issue model"""
    __tablename__ = "issues"
    
    issue_id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.order_id", ondelete="SET NULL"))
    customer_id = Column(Integer, ForeignKey("customers.customer_id", ondelete="SET NULL"))
    employee_id = Column(Integer, ForeignKey("employees.employee_id", ondelete="SET NULL"))
    created_at = Column(TIMESTAMP(timezone=False), server_default=func.now())
    closed_at = Column(TIMESTAMP(timezone=False))
    status = Column(String(30))  # مفتوحة/مغلقة/قيد المعالجة...
    category = Column(String(100))  # تصنيف المشكلة (توصيل، جودة، دفع...)
    root_cause = Column(Text)  # السبب الجذري
    resolution = Column(Text)  # طريقة الحل
    ai_classification = Column(Text)  # تصنيف الذكاء الاصطناعي
    employee_note = Column(Text)  # ملاحظة الموظف النهائية
    
    # Relationships
    order = relationship("Order", back_populates="issues")
    customer = relationship("Customer")
    employee = relationship("Employee", back_populates="issues")
    notes = relationship("Note", back_populates="issue")
    call_logs = relationship("CallLog", back_populates="issue") 