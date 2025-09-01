import React, { useState } from 'react';
import { useNotifications, type Notification } from '../store/notifications';

interface NotificationInboxProps {
  tab: string;
  className?: string;
}

const NotificationInbox: React.FC<NotificationInboxProps> = ({ tab, className = '' }) => {
  const { notifications, markTabAsSeen, getUnseenCount, clearTab } = useNotifications();
  const [isOpen, setIsOpen] = useState(false);

  const tabNotifications = notifications[tab] || [];
  const unseenCount = getUnseenCount(tab);

  const handleToggle = () => {
    if (!isOpen && unseenCount > 0) {
      markTabAsSeen(tab);
    }
    setIsOpen(!isOpen);
  };

  const formatTime = (date: Date) => {
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffMins < 1) return 'الآن';
    if (diffMins < 60) return `${diffMins} د`;
    if (diffHours < 24) return `${diffHours} س`;
    return `${diffDays} ي`;
  };

  const getTypeIcon = (type: Notification['type']) => {
    switch (type) {
      case 'order_created': return '📝';
      case 'status_changed': return '🔄';
      case 'captain_assigned': return '👨‍✈️';
      case 'problem_reported': return '⚠️';
      default: return '📢';
    }
  };

  return (
    <div className={`relative ${className}`}>
      {/* Bell Icon with Badge */}
      <button
        onClick={handleToggle}
        className={`relative p-2 rounded-lg transition-colors ${
          unseenCount > 0 
            ? 'bg-red-100 text-red-600 hover:bg-red-200' 
            : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
        }`}
        title={`${tabNotifications.length} إشعارات${unseenCount > 0 ? ` (${unseenCount} غير مقروء)` : ''}`}
      >
        <span className={`text-xl ${unseenCount > 0 ? 'animate-pulse' : ''}`}>
          🔔
        </span>
        
        {/* Badge */}
        {unseenCount > 0 && (
          <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center animate-pulse">
            {unseenCount > 9 ? '9+' : unseenCount}
          </span>
        )}
      </button>

      {/* Dropdown */}
      {isOpen && (
        <>
          {/* Backdrop */}
          <div 
            className="fixed inset-0 z-10" 
            onClick={() => setIsOpen(false)}
          />
          
          {/* Notifications Panel */}
          <div className="absolute right-0 mt-2 w-80 bg-white rounded-lg shadow-lg border z-20 max-h-96 overflow-hidden">
            {/* Header */}
            <div className="p-3 border-b bg-gray-50 flex items-center justify-between">
              <h3 className="font-medium text-gray-900">
                الإشعارات ({tabNotifications.length})
              </h3>
              {tabNotifications.length > 0 && (
                <button
                  onClick={() => clearTab(tab)}
                  className="text-xs text-red-600 hover:text-red-700"
                >
                  مسح الكل
                </button>
              )}
            </div>

            {/* Notifications List */}
            <div className="max-h-80 overflow-y-auto">
              {tabNotifications.length === 0 ? (
                <div className="p-4 text-center text-gray-500 text-sm">
                  لا توجد إشعارات
                </div>
              ) : (
                tabNotifications.map((notification) => (
                  <div
                    key={notification.id}
                    className={`p-3 border-b border-gray-100 hover:bg-gray-50 transition-colors ${
                      notification.unseen ? 'bg-blue-50 border-l-4 border-l-blue-500' : ''
                    }`}
                  >
                    <div className="flex items-start gap-3">
                      {/* Icon */}
                      <span className="text-lg flex-shrink-0 mt-0.5">
                        {getTypeIcon(notification.type)}
                      </span>
                      
                      {/* Content */}
                      <div className="flex-1 min-w-0">
                        <p className="font-medium text-sm text-gray-900 truncate">
                          {notification.title}
                        </p>
                        <p className="text-xs text-gray-600 mt-1 line-clamp-2">
                          {notification.message}
                        </p>
                        <p className="text-xs text-gray-400 mt-1">
                          {formatTime(notification.timestamp)}
                        </p>
                      </div>

                      {/* Unseen Indicator */}
                      {notification.unseen && (
                        <div className="w-2 h-2 bg-blue-500 rounded-full flex-shrink-0 mt-2" />
                      )}
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default NotificationInbox;
