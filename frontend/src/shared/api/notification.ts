/** Cliente API para notificaciones internas (BE-013).
 * 
 * Implementa operaciones tipadas sobre el endpoint del slice.
 */
import { resolveApiBase } from './api-base';

const API_BASE = resolveApiBase();

export interface Notification {
  id: number;
  clinic_id: number;
  user_id: number | null;
  event_type: string;
  subject: string;
  body: string;
  ref_type: string | null;
  ref_id: number | null;
  is_read: boolean;
  read_at: string | null;
  created_at: string;
}

export interface NotificationMeta {
  page: number;
  page_size: number;
  total: number;
  pages: number;
  unread_only: boolean;
}

export interface NotificationList {
  items: Notification[];
  meta: NotificationMeta;
}

export interface UnreadCount {
  unread: number;
}

export interface NotificationServiceError {
  status: number;
  detail: string;
}

/**
 * Listar notificaciones del usuario autenticado.
 * 
 * @param page - Número de página (1-based)
 * @param pageSize - Tamaño de página (entre 1 y 100)
 * @param unreadOnly - Solo notificaciones no leídas
 * @returns Lista paginada de notificaciones
 */
export async function listNotifications(
  page: number = 1,
  pageSize: number = 20,
  unreadOnly: boolean = false,
): Promise<NotificationList> {
  const params = new URLSearchParams({
    page: page.toString(),
    page_size: pageSize.toString(),
    unread_only: unreadOnly.toString(),
  });

  const response = await fetch(`${API_BASE}/notifications?${params}`, {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Error desconocido' }));
    throw { status: response.status, detail: error.detail || 'Error al listar notificaciones' } as NotificationServiceError;
  }

  return response.json();
}

/**
 * Contar notificaciones no leídas del usuario autenticado.
 * 
 * @returns Cantidad de notificaciones no leídas
 */
export async function getUnreadCount(): Promise<UnreadCount> {
  const response = await fetch(`${API_BASE}/notifications/count/unread`, {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Error desconocido' }));
    throw { status: response.status, detail: error.detail || 'Error al obtener cuenta de notificaciones' } as NotificationServiceError;
  }

  return response.json();
}

/**
 * Marcar una notificación como leída.
 * 
 * @param notificationId - ID de la notificación
 * @returns La notificación actualizada
 */
export async function markNotificationRead(notificationId: number): Promise<Notification> {
  const response = await fetch(`${API_BASE}/notifications/${notificationId}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Error desconocido' }));
    throw { status: response.status, detail: error.detail || 'Error al marcar notificación como leída' } as NotificationServiceError;
  }

  return response.json();
}

/**
 * Marcar todas las notificaciones como leídas.
 * 
 * @returns Cantidad de notificaciones marcadas como leídas
 */
export async function markAllNotificationsRead(): Promise<{ read: number }> {
  const response = await fetch(`${API_BASE}/notifications/read-all`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Error desconocido' }));
    throw { status: response.status, detail: error.detail || 'Error al marcar todas las notificaciones como leídas' } as NotificationServiceError;
  }

  return response.json();
}