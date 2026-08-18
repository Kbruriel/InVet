import { getAccessToken } from '@/shared/auth/session';

import { resolveApiBase } from './api-base';

const API_BASE = resolveApiBase();

export interface ApiError {
  status: number;
  detail: string;
}

type RequestBody = BodyInit | object | undefined;

function buildHeaders(extra?: HeadersInit): Headers {
  const headers = new Headers(extra);
  headers.set('Content-Type', 'application/json');

  const token = getAccessToken();
  if (token && !headers.has('Authorization')) {
    headers.set('Authorization', `Bearer ${token}`);
  }

  return headers;
}

function serializeBody(body: RequestBody): BodyInit | undefined {
  if (body === undefined) {
    return undefined;
  }

  if (
    typeof body === 'string' ||
    body instanceof FormData ||
    body instanceof URLSearchParams ||
    body instanceof Blob ||
    body instanceof ArrayBuffer ||
    ArrayBuffer.isView(body)
  ) {
    return body as BodyInit;
  }

  return JSON.stringify(body);
}

async function parseResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const error = (await response.json().catch(() => ({ detail: 'Error desconocido' }))) as {
      detail?: string;
    };
    throw {
      status: response.status,
      detail: error.detail || `HTTP ${response.status}`,
    } as ApiError;
  }

  if (response.status === 204) {
    return undefined as T;
  }

  const text = await response.text();
  if (!text) {
    return undefined as T;
  }

  return JSON.parse(text) as T;
}

async function request<T>(
  method: string,
  path: string,
  body?: RequestBody,
  extraHeaders?: HeadersInit,
): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    method,
    headers: buildHeaders(extraHeaders),
    body: serializeBody(body),
  });

  return parseResponse<T>(response);
}

export const apiClient = {
  get<T>(path: string, extraHeaders?: HeadersInit): Promise<T> {
    return request<T>('GET', path, undefined, extraHeaders);
  },
  post<T>(path: string, body?: RequestBody, extraHeaders?: HeadersInit): Promise<T> {
    return request<T>('POST', path, body, extraHeaders);
  },
  put<T>(path: string, body?: RequestBody, extraHeaders?: HeadersInit): Promise<T> {
    return request<T>('PUT', path, body, extraHeaders);
  },
  delete<T>(path: string, extraHeaders?: HeadersInit): Promise<T> {
    return request<T>('DELETE', path, undefined, extraHeaders);
  },
};
