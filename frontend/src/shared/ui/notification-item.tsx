import { Notification } from '@/shared/api/notification';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';

interface NotificationItemProps {
  notification: Notification;
  onMarkAsRead: (id: number) => void;
}

export function NotificationItem({ notification, onMarkAsRead }: NotificationItemProps) {
  const handleMarkAsRead = () => {
    if (!notification.is_read) {
      onMarkAsRead(notification.id);
    }
  };

  return (
    <div 
      className={`p-4 rounded-lg border transition-colors ${
        notification.is_read 
          ? 'bg-gray-50 border-gray-200' 
          : 'bg-white border-teal-300 shadow-sm hover:shadow-md'
      }`}
    >
      <div className="flex justify-between items-start">
        <div>
          <h3 className={`font-semibold ${notification.is_read ? 'text-gray-700' : 'text-teal-800'}`}>
            {notification.subject}
          </h3>
          <p className="text-gray-600 mt-1">{notification.body}</p>
        </div>
        {!notification.is_read && (
          <button 
            onClick={handleMarkAsRead}
            className="text-xs px-2 py-1 bg-teal-100 text-teal-800 rounded hover:bg-teal-200 transition-colors"
          >
            Marcar como leída
          </button>
        )}
      </div>
      
      <div className="flex justify-between items-center mt-3">
        <span className="text-xs text-gray-500">
          {format(new Date(notification.created_at), 'dd/MM/yyyy', { locale: es })}
        </span>
        <span className="text-xs px-2 py-1 bg-gray-200 text-gray-700 rounded-full">
          {notification.event_type}
        </span>
      </div>
    </div>
  );
}