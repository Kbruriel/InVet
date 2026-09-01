'use client';

import { useState, useEffect } from 'react';
import { Notification, listNotifications, markNotificationRead, markAllNotificationsRead } from '@/shared/api/notification';
import { EmptyState } from '@/shared/ui/components/EmptyState';
import { LoadingSpinner } from '@/shared/ui/loading-spinner';
import { ErrorAlert as ErrorBanner } from '@/shared/ui/error-alert';

export interface NotificationTab {
  id: 'all' | 'unread';
  label: string;
}

interface ApiResponse {
  items: Notification[];
  meta: { pages: number };
}

export function NotificationCenter() {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'all' | 'unread'>('all');

  const tabs: NotificationTab[] = [
    { id: 'all', label: 'Todas' },
    { id: 'unread', label: 'No leídas' }
  ];

  useEffect(() => {
    setError(null);
    loadNotifications();
  }, [activeTab]);

  const loadNotifications = async () => {
    try {
      setIsLoading(true);
      
      const response: ApiResponse = await listNotifications(1, 20, activeTab === 'unread');
      setNotifications(response.items);
    } catch (err) {
      const message = typeof err === 'object' && err !== null && 'detail' in (err as Record<string, unknown>)
        ? String((err as Record<string, unknown>).detail)
        : 'Error desconocido';
      setError('Error al cargar notificaciones: ' + message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleMarkAsRead = async (notificationId: number) => {
    try {
      await markNotificationRead(notificationId);
      
      // Update local state
      setNotifications(prev => 
        prev.map(n => 
          n.id === notificationId ? { ...n, is_read: true } : n
        )
      );
    } catch {
      setError('Error al marcar notificación como leída');
    }
  };

  const handleMarkAllAsRead = async () => {
    try {
      await markAllNotificationsRead();
      
      // Update local state
      setNotifications(prev => 
        prev.map(n => ({ ...n, is_read: true }))
      );
    } catch {
      setError('Error al marcar todas las notificaciones como leídas');
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner data-testid="loading-spinner" />
      </div>
    );
  }

  if (error) {
    return <ErrorBanner message={error} />;
  }

  if (notifications.length === 0) {
    return (
      <div className="py-8">
        <EmptyState 
          title="Sin notificaciones recientes"
          description="No tienes notificaciones en este momento."
        />
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Tabs */}
      <div className="flex border-b border-gray-200">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            className={`px-4 py-2 font-medium text-sm ${
              activeTab === tab.id
                ? 'text-teal-600 border-b-2 border-teal-600'
                : 'text-gray-500 hover:text-gray-700'
            }`}
            onClick={() => setActiveTab(tab.id)}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Notification List */}
      <ul className="divide-y divide-gray-200">
        {notifications.map((notification) => (
          <li 
            key={notification.id} 
            className={`p-4 hover:bg-gray-50 transition-colors ${
              !notification.is_read ? 'bg-blue-50' : ''
            }`}
          >
            <div className="flex items-start">
              <div className="flex-1 min-w-0">
                <h3 className="text-sm font-medium text-gray-900 truncate">
                  {notification.subject}
                </h3>
                <p 
                  className={`mt-1 text-sm ${
                    notification.is_read ? 'text-gray-500' : 'text-gray-900'
                  }`}
                >
                  {notification.body}
                </p>
                <div className="mt-2 flex items-center text-xs text-gray-400">
                  <span>{new Date(notification.created_at).toLocaleDateString()}</span>
                  <span className="mx-1">•</span>
                  <span>Evento: {notification.event_type}</span>
                </div>
              </div>
                            {!notification.is_read ? (
                <button
                  onClick={() => handleMarkAsRead(notification.id)}
                  className="ml-4 inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded-full bg-teal-100 text-teal-800 hover:bg-teal-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-teal-500"
                >
                  Marcar como leída
                </button>
              ) : (
                <span className="ml-4 inline-flex items-center px-3 py-1.5 text-xs font-medium rounded-full bg-gray-100 text-gray-800">
                  Leída
                </span>
              )}
            </div>
          </li>        ))}
      </ul>

      {/* Mark All as Read Button */}
      <div className="flex justify-end mt-4">
        <button
          onClick={handleMarkAllAsRead}
          className="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded-full bg-teal-600 text-white hover:bg-teal-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-teal-500"
        >
          Marcar todas como leídas
        </button>
      </div>
    </div>
  );
}
