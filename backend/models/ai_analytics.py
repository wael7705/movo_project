"""
AI Analytics models
نماذج تحليلات الذكاء الاصطناعي
"""

from sqlalchemy import Column, Integer, String, ForeignKey, Text, TIMESTAMP, Boolean, DECIMAL, Interval, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database.config import Base


class AIDecisionLog(Base):
    """AI Decision Log model"""
    __tablename__ = "ai_decisions_log"
    
    decision_id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.order_id", ondelete="CASCADE"))
    decision_type = Column(String(50), nullable=False)  # نوع القرار: reassign_captain, cancel_order, delay_order, optimize_route, etc.
    decision_result = Column(String(30), nullable=False)  # نتيجة القرار: approved, denied, pending, executed, failed
    decision_timestamp = Column(TIMESTAMP(timezone=False), server_default=func.now())
    ai_model_version = Column(String(20))  # إصدار نموذج الذكاء الاصطناعي المستخدم
    confidence_score = Column(DECIMAL(3, 2))  # درجة الثقة في القرار (0-1)
    reasoning = Column(Text)  # شرح منطق القرار
    notes = Column(Text)  # ملاحظات إضافية
    execution_duration = Column(Interval)  # مدة تنفيذ القرار
    affected_entities = Column(JSON)  # الكيانات المتأثرة بالقرار (captain_id, restaurant_id, etc.)
    
    # Relationships
    order = relationship("Order", back_populates="ai_decisions")


class AIFailure(Base):
    """AI Failure model"""
    __tablename__ = "ai_failures"
    
    failure_id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.order_id", ondelete="SET NULL"))  # يمكن أن يكون فشل عام غير مرتبط بطلب معين
    failure_module = Column(String(50), nullable=False)  # الوحدة التي حدث فيها الفشل: nlp, call_logic, route_optimization, etc.
    error_code = Column(String(20))  # كود الخطأ
    error_message = Column(Text, nullable=False)  # رسالة الخطأ التفصيلية
    failure_timestamp = Column(TIMESTAMP(timezone=False), server_default=func.now())
    is_resolved = Column(Boolean, default=False)  # هل تم حل المشكلة؟
    resolution_timestamp = Column(TIMESTAMP(timezone=False))  # وقت حل المشكلة
    resolution_method = Column(String(100))  # طريقة الحل
    resolution_notes = Column(Text)  # ملاحظات حول الحل
    ai_model_version = Column(String(20))  # إصدار النموذج عند حدوث الفشل
    stack_trace = Column(Text)  # تفاصيل تقنية للفشل (للمطورين)
    severity_level = Column(String(20), default="medium")  # مستوى خطورة الفشل: low, medium, high, critical
    
    # Relationships
    order = relationship("Order", back_populates="ai_failures")


class AlertLog(Base):
    """Alert Log model"""
    __tablename__ = "alerts_log"
    
    alert_id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.order_id", ondelete="CASCADE"))
    alert_type = Column(String(50), nullable=False)  # نوع التنبيه: delayed_order, abnormal_behavior, system_issue, etc.
    alert_level = Column(String(20), nullable=False, default="info")  # مستوى التنبيه: info, warning, error, critical
    alert_message = Column(Text, nullable=False)  # رسالة التنبيه
    alert_data = Column(JSON)  # بيانات إضافية للتنبيه
    created_at = Column(TIMESTAMP(timezone=False), server_default=func.now())
    resolved_at = Column(TIMESTAMP(timezone=False))  # وقت حل التنبيه
    is_resolved = Column(Boolean, default=False)  # هل تم حل التنبيه؟
    resolved_by = Column(Integer, ForeignKey("employees.employee_id", ondelete="SET NULL"))  # الموظف الذي حل التنبيه
    resolution_notes = Column(Text)  # ملاحظات الحل
    auto_resolved = Column(Boolean, default=False)  # هل تم الحل تلقائياً؟
    escalation_level = Column(Integer, default=0)  # مستوى التصعيد (0 = لا تصعيد، 1+ = مستويات التصعيد)
    
    # Relationships
    order = relationship("Order", back_populates="alerts")
    resolved_by_employee = relationship("Employee", back_populates="alerts_resolved") 