"""
Notification service for sending notifications
خدمة الإشعارات لإرسال الإشعارات
"""

from typing import Dict, Any, List
from datetime import datetime
import json


class NotificationService:
    """Service for notification-related operations"""
    
    def __init__(self):
        self.notification_history = []
    
    def send_notification(self, user_id: int, user_type: str, title: str, message: str, 
                         notification_type: str = "info") -> Dict[str, Any]:
        """
        Send a notification to a user
        إرسال إشعار للمستخدم
        """
        try:
            notification = {
                "id": len(self.notification_history) + 1,
                "user_id": user_id,
                "user_type": user_type,
                "title": title,
                "message": message,
                "type": notification_type,
                "is_read": False,
                "created_at": datetime.now().isoformat()
            }
            
            self.notification_history.append(notification)
            
            # In a real implementation, this would send to a notification service
            # مثل Firebase Cloud Messaging أو OneSignal
            print(f"📱 Notification sent: {title} - {message}")
            
            return {
                "success": True,
                "notification_id": notification["id"],
                "message": "Notification sent successfully"
            }
            
        except Exception as e:
            print(f"Error sending notification: {e}")
            return {"error": str(e)}
    
    def send_order_status_notification(self, order_id: int, user_id: int, user_type: str, 
                                     status: str) -> Dict[str, Any]:
        """
        Send order status update notification
        إرسال إشعار تحديث حالة الطلب
        """
        status_messages = {
            "confirmed": {
                "title": "تم تأكيد طلبك",
                "message": f"تم تأكيد طلبك رقم #{order_id} وسيتم تجهيزه قريباً"
            },
            "preparing": {
                "title": "جاري تجهيز طلبك",
                "message": f"طلبك رقم #{order_id} قيد التجهيز"
            },
            "delivering": {
                "title": "طلبك في الطريق",
                "message": f"طلبك رقم #{order_id} في الطريق إليك"
            },
            "delivered": {
                "title": "تم توصيل طلبك",
                "message": f"تم توصيل طلبك رقم #{order_id} بنجاح"
            },
            "cancelled": {
                "title": "تم إلغاء طلبك",
                "message": f"تم إلغاء طلبك رقم #{order_id}"
            }
        }
        
        if status in status_messages:
            return self.send_notification(
                user_id=user_id,
                user_type=user_type,
                title=status_messages[status]["title"],
                message=status_messages[status]["message"],
                notification_type="order_status"
            )
        else:
            return {"error": "Invalid status"}
    
    def send_delivery_fee_notification(self, order_id: int, user_id: int, fee: float) -> Dict[str, Any]:
        """
        Send delivery fee notification
        إرسال إشعار رسوم التوصيل
        """
        return self.send_notification(
            user_id=user_id,
            user_type="customer",
            title="رسوم التوصيل",
            message=f"رسوم التوصيل لطلبك رقم #{order_id}: {fee} ريال",
            notification_type="delivery_fee"
        )
    
    def send_weather_alert(self, city: str, weather_condition: str, 
                          affected_orders: List[int]) -> Dict[str, Any]:
        """
        Send weather alert notification
        إرسال إشعار تنبيه الطقس
        """
        message = f"تنبيه طقس في {city}: {weather_condition}. قد يؤثر على أوقات التوصيل."
        
        # Send to all affected orders
        results = []
        for order_id in affected_orders:
            # In real implementation, get user_id from order
            result = self.send_notification(
                user_id=order_id,  # This should be actual user_id
                user_type="customer",
                title="تنبيه الطقس",
                message=message,
                notification_type="weather_alert"
            )
            results.append(result)
        
        return {
            "success": True,
            "affected_orders": len(affected_orders),
            "results": results
        }
    
    def get_user_notifications(self, user_id: int, user_type: str, 
                             limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get notifications for a user
        الحصول على إشعارات المستخدم
        """
        try:
            user_notifications = [
                notif for notif in self.notification_history
                if notif["user_id"] == user_id and notif["user_type"] == user_type
            ]
            
            # Sort by creation time (newest first)
            user_notifications.sort(key=lambda x: x["created_at"], reverse=True)
            
            return user_notifications[:limit]
            
        except Exception as e:
            print(f"Error getting user notifications: {e}")
            return []
    
    def mark_as_read(self, notification_id: int) -> Dict[str, Any]:
        """
        Mark a notification as read
        تحديد إشعار كمقروء
        """
        try:
            for notification in self.notification_history:
                if notification["id"] == notification_id:
                    notification["is_read"] = True
                    return {"success": True, "notification_id": notification_id}
            
            return {"error": "Notification not found"}
            
        except Exception as e:
            print(f"Error marking notification as read: {e}")
            return {"error": str(e)}
    
    def get_unread_count(self, user_id: int, user_type: str) -> int:
        """
        Get count of unread notifications for a user
        الحصول على عدد الإشعارات غير المقروءة للمستخدم
        """
        try:
            unread_count = sum(
                1 for notif in self.notification_history
                if notif["user_id"] == user_id 
                and notif["user_type"] == user_type 
                and not notif["is_read"]
            )
            
            return unread_count
            
        except Exception as e:
            print(f"Error getting unread count: {e}")
            return 0 