'use client';

import { useState, useEffect } from 'react';
import { getUnreadCount } from '@/shared/api/notification';

export function NotificationBadge() {
  const [unreadCount, setUnreadCount] = useState<number>(0);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    const loadUnreadCount = async () => {
      try {
        setIsLoading(true);
        const response = await getUnreadCount();
        setUnreadCount(response.unread);
      } catch (err) {
        console.error('Error loading unread count:', err);
      } finally {
        setIsLoading(false);
      }
    };

    loadUnreadCount();
  }, []);

  if (isLoading || unreadCount === 0) {
    return null;
  }

  return (
    <span 
      className="inline-flex items-center justify-center px-2 py-1 text-xs font-bold leading-none text-white bg-red-600 rounded-full"
      aria-label={`${unreadCount} notificaciones sin leer`}
    >
      {unreadCount}
    </span>
  );
}