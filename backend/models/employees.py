"""
Employee models
نماذج الموظفين
"""

from sqlalchemy import Column, Integer, String, ForeignKey, Text, Boolean, DECIMAL, Date, JSON
from sqlalchemy.orm import relationship
from ..database.config import Base
from .enums import EmployeeRoleEnum


class Employee(Base):
    """Employee model"""
    __tablename__ = "employees"
    
    employee_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    phone = Column(String(20))
    department = Column(String(50))  # قسم العمل (دعم العملاء، المبيعات، التقنية...)
    position = Column(String(50))  # المنصب الوظيفي
    role = Column(String(20), default=EmployeeRoleEnum.STAFF)  # دور الموظف في النظام
    hire_date = Column(Date, nullable=False)
    is_active = Column(Boolean, default=True)
    
    # حقول تقييم الأداء
    total_calls_handled = Column(Integer, default=0)  # إجمالي المكالمات المعالجة
    successful_calls = Column(Integer, default=0)  # المكالمات الناجحة
    failed_calls = Column(Integer, default=0)  # المكالمات الفاشلة
    avg_call_duration = Column(String(50))  # متوسط مدة المكالمة
    total_issues_resolved = Column(Integer, default=0)  # إجمالي المشاكل المحلولة
    avg_issue_resolution_time = Column(String(50))  # متوسط وقت حل المشكلة
    customer_satisfaction_score = Column(DECIMAL(3, 2), default=0.00)  # درجة رضا العملاء (0-5)
    ai_performance_score = Column(DECIMAL(3, 2), default=0.00)  # تقييم الذكاء الاصطناعي للأداء (0-5)
    efficiency_rating = Column(DECIMAL(3, 2), default=0.00)  # تقييم الكفاءة العامة
    
    # حقول إضافية للتحليل
    last_performance_review = Column(Date)  # آخر تقييم أداء
    performance_notes = Column(Text)  # ملاحظات التقييم
    ai_learning_data = Column(JSON)  # بيانات تعلم الذكاء الاصطناعي
    
    # Relationships
    issues = relationship("Issue", back_populates="employee")
    call_logs = relationship("CallLog", back_populates="employee")
    alerts_resolved = relationship("AlertLog", back_populates="resolved_by_employee") 