import { env } from "@/shared/config/env";

export class ApiError extends Error {
  status: number;
  payload: unknown;

  constructor(status: number, message: string, payload: unknown) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.payload = payload;
  }
}

type JsonRecord = Record<string, unknown>;

function buildUrl(path: string) {
  if (path.startsWith("http://") || path.startsWith("https://")) {
    return path;
  }

  return `${env.apiBaseUrl}${path.startsWith("/") ? path : `/${path}`}`;
}

async function parsePayload(response: Response) {
  const contentType = response.headers.get("content-type") ?? "";

  if (contentType.includes("application/json")) {
    return response.json();
  }

  return response.text();
}

function getErrorMessage(status: number, payload: unknown) {
  if (payload && typeof payload === "object") {
    const detail = (payload as JsonRecord).detail;
    if (typeof detail === "string" && detail.length > 0) {
      return detail;
    }
  }

  return `La solicitud fallo con estado ${status}.`;
}

export async function apiGet<T>(path: string, init?: RequestInit) {
  const response = await fetch(buildUrl(path), {
    ...init,
    method: "GET",
    headers: {
      Accept: "application/json",
      ...(init?.headers ?? {}),
    },
  });

  const payload = await parsePayload(response);

  if (!response.ok) {
    throw new ApiError(response.status, getErrorMessage(response.status, payload), payload);
  }

  return payload as T;
}

type ApiRootResponse = {
  message?: string;
};

export async function getApiRoot() {
  return apiGet<ApiRootResponse>("/api/v1/");
}
