'use client';

import { useEffect, useState } from 'react';
import { listNotifications, getUnreadCount, Notification, markNotificationRead, markAllNotificationsRead } from '@/shared/api/notification';
import { NotificationItem } from '@/shared/ui/notification-item';
import { LoadingSpinner } from '@/shared/ui/loading-spinner';
import { ErrorAlert } from '@/shared/ui/error-alert';

export default function NotificationsPage() {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [unreadCount, setUnreadCount] = useState<number>(0);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState<number>(1);
  const [hasMore, setHasMore] = useState<boolean>(true);

  const pageSize = 20;

  // Load notifications and unread count
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const [notificationList, countResponse] = await Promise.all([
          listNotifications(page, pageSize),
          getUnreadCount()
        ]);
        
        setNotifications(notificationList.items);
        setUnreadCount(countResponse.unread);
        setHasMore(notificationList.meta.pages > page);
      } catch (err) {
        setError('Error al cargar las notificaciones');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [page]);

  const handleMarkAsRead = async (notificationId: number) => {
    try {
      const updatedNotification = await markNotificationRead(notificationId);
      setNotifications(notifications.map(n => 
        n.id === notificationId ? { ...n, is_read: true, read_at: updatedNotification.read_at } : n
      ));
      setUnreadCount(prev => Math.max(0, prev - 1));
    } catch (err) {
      setError('Error al marcar notificación como leída');
      console.error(err);
    }
  };

  const handleMarkAllAsRead = async () => {
    try {
      await markAllNotificationsRead();
      setNotifications(notifications.map(n => ({ ...n, is_read: true })));
      setUnreadCount(0);
    } catch (err) {
      setError('Error al marcar todas las notificaciones como leídas');
      console.error(err);
    }
  };

  const handleLoadMore = () => {
    setPage(prev => prev + 1);
  };

  if (loading && notifications.length === 0) {
    return <div className="flex justify-center items-center h-64"><LoadingSpinner /></div>;
  }

  if (error) {
    return <ErrorAlert message={error} />;
  }

  return (
    <div className="max-w-4xl mx-auto p-4">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-800">Notificaciones</h1>
        {unreadCount > 0 && (
          <button 
            onClick={handleMarkAllAsRead}
            className="px-4 py-2 bg-teal-600 text-white rounded-md hover:bg-teal-700 transition-colors"
          >
            Marcar todas como leídas
          </button>
        )}
      </div>

      {notifications.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-600">No hay notificaciones</p>
        </div>
      ) : (
        <div className="space-y-4">
          {notifications.map(notification => (
            <NotificationItem
              key={notification.id}
              notification={notification}
              onMarkAsRead={handleMarkAsRead}
            />
          ))}
          
          {hasMore && (
            <div className="flex justify-center mt-6">
              <button
                onClick={handleLoadMore}
                className="px-4 py-2 bg-gray-200 text-gray-800 rounded-md hover:bg-gray-300 transition-colors"
              >
                Cargar más
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
