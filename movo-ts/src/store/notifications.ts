import { useState, useEffect } from 'react';

export interface Notification {
  id: string;
  type: 'order_created' | 'status_changed' | 'captain_assigned' | 'problem_reported';
  title: string;
  message: string;
  timestamp: Date;
  tab: 'pending' | 'processing' | 'out_for_delivery' | 'delivered' | 'problem';
  orderId?: number;
  unseen: boolean;
}

const MAX_NOTIFICATIONS_PER_TAB = 5;

// Get stored notifications from localStorage
function getStoredNotifications(): Record<string, Notification[]> {
  try {
    const stored = localStorage.getItem('movo_notifications');
    if (stored) {
      const parsed = JSON.parse(stored);
      // Convert timestamp strings back to Date objects
      Object.keys(parsed).forEach(tab => {
        parsed[tab] = parsed[tab].map((notif: any) => ({
          ...notif,
          timestamp: new Date(notif.timestamp)
        }));
      });
      return parsed;
    }
  } catch (error) {
    console.error('Error loading notifications from localStorage:', error);
  }
  return {
    pending: [],
    processing: [],
    out_for_delivery: [],
    delivered: [],
    problem: []
  };
}

// Store notifications to localStorage
function storeNotifications(notifications: Record<string, Notification[]>) {
  try {
    localStorage.setItem('movo_notifications', JSON.stringify(notifications));
  } catch (error) {
    console.error('Error saving notifications to localStorage:', error);
  }
}

// Custom hook for notifications
export function useNotifications() {
  const [notifications, setNotifications] = useState<Record<string, Notification[]>>(getStoredNotifications);

  // Add new notification
  const addNotification = (notification: Omit<Notification, 'id' | 'timestamp' | 'unseen'>) => {
    const newNotification: Notification = {
      ...notification,
      id: `${Date.now()}_${Math.random().toString(36).substring(2)}`,
      timestamp: new Date(),
      unseen: true
    };

    setNotifications(prev => {
      const updated = { ...prev };
      const tabNotifications = [...(updated[notification.tab] || [])];
      
      // Remove duplicates by orderId if exists
      if (newNotification.orderId) {
        const existingIndex = tabNotifications.findIndex(
          n => n.orderId === newNotification.orderId && n.type === newNotification.type
        );
        if (existingIndex !== -1) {
          tabNotifications.splice(existingIndex, 1);
        }
      }
      
      // Add new notification at the beginning
      tabNotifications.unshift(newNotification);
      
      // Keep only last 5 notifications
      if (tabNotifications.length > MAX_NOTIFICATIONS_PER_TAB) {
        tabNotifications.splice(MAX_NOTIFICATIONS_PER_TAB);
      }
      
      updated[notification.tab] = tabNotifications;
      storeNotifications(updated);
      return updated;
    });
  };

  // Mark notifications as seen for a specific tab
  const markTabAsSeen = (tab: string) => {
    setNotifications(prev => {
      const updated = { ...prev };
      if (updated[tab]) {
        updated[tab] = updated[tab].map(n => ({ ...n, unseen: false }));
        storeNotifications(updated);
      }
      return updated;
    });
  };

  // Get unseen count for a tab
  const getUnseenCount = (tab: string): number => {
    return (notifications[tab] || []).filter(n => n.unseen).length;
  };

  // Get total unseen count
  const getTotalUnseenCount = (): number => {
    return Object.values(notifications).flat().filter(n => n.unseen).length;
  };

  // Clear all notifications for a tab
  const clearTab = (tab: string) => {
    setNotifications(prev => {
      const updated = { ...prev };
      updated[tab] = [];
      storeNotifications(updated);
      return updated;
    });
  };

  return {
    notifications,
    addNotification,
    markTabAsSeen,
    getUnseenCount,
    getTotalUnseenCount,
    clearTab
  };
}

// WebSocket message handler
export function handleWebSocketMessage(message: any, addNotification: (notif: Omit<Notification, 'id' | 'timestamp' | 'unseen'>) => void) {
  try {
    // Handle different message types
    switch (message.type) {
      case 'order_created':
        addNotification({
          type: 'order_created',
          title: 'طلب جديد',
          message: `تم إنشاء طلب رقم ${message.order_id}`,
          tab: 'pending',
          orderId: message.order_id
        });
        break;

      case 'status_changed':
        const statusMap: Record<string, { tab: string; title: string }> = {
          'pending': { tab: 'pending', title: 'في الانتظار' },
          'processing': { tab: 'processing', title: 'قيد المعالجة' },
          'out_for_delivery': { tab: 'out_for_delivery', title: 'خرج للتوصيل' },
          'delivered': { tab: 'delivered', title: 'تم التوصيل' },
          'problem': { tab: 'problem', title: 'مشكلة' },
        };

        const statusInfo = statusMap[message.new_status];
        if (statusInfo) {
          addNotification({
            type: 'status_changed',
            title: `تغير الحالة: ${statusInfo.title}`,
            message: `طلب رقم ${message.order_id} تغيرت حالته إلى ${statusInfo.title}`,
            tab: statusInfo.tab as any,
            orderId: message.order_id
          });
        }
        break;

      case 'captain_assigned':
        addNotification({
          type: 'captain_assigned',
          title: 'تم تعيين كابتن',
          message: `تم تعيين ${message.captain_name} للطلب رقم ${message.order_id}`,
          tab: 'processing',
          orderId: message.order_id
        });
        break;

      case 'problem_reported':
        addNotification({
          type: 'problem_reported',
          title: 'تم الإبلاغ عن مشكلة',
          message: `طلب رقم ${message.order_id} يحتاج انتباه`,
          tab: 'problem',
          orderId: message.order_id
        });
        break;

      default:
        // Generic notification for unknown types
        if (message.order_id) {
          addNotification({
            type: 'order_created',
            title: 'تحديث الطلب',
            message: `تحديث على طلب رقم ${message.order_id}`,
            tab: 'pending',
            orderId: message.order_id
          });
        }
        break;
    }
  } catch (error) {
    console.error('Error handling WebSocket message:', error);
  }
}
