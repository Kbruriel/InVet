import { NextRequest, NextResponse } from 'next/server';

const BACKEND_BASE_URL = process.env.BACKEND_INTERNAL_URL || 'http://127.0.0.1:8000';

async function proxyRequest(
  request: NextRequest,
  context: { params?: { path?: string[] } },
) {
  const path = context.params?.path?.join('/') || '';
  const url = new URL(
    `${BACKEND_BASE_URL}/api/v1${path ? `/${path}` : ''}${request.nextUrl.search}`,
  );

  const headers = new Headers(request.headers);
  headers.delete('host');
  headers.delete('connection');
  headers.delete('content-length');
  headers.delete('accept-encoding');

  const method = request.method.toUpperCase();
  const body = method === 'GET' || method === 'HEAD' ? undefined : await request.text();

  try {
    const backendResponse = await fetch(url, {
      method,
      headers,
      body,
      redirect: 'manual',
    });

    const responseHeaders = new Headers(backendResponse.headers);
    responseHeaders.delete('content-encoding');
    responseHeaders.delete('transfer-encoding');

    return new NextResponse(backendResponse.body, {
      status: backendResponse.status,
      headers: responseHeaders,
    });
  } catch {
    return NextResponse.json(
      { detail: 'Servicio temporalmente no disponible' },
      { status: 503 },
    );
  }
}

export async function GET(
  request: NextRequest,
  context: { params?: { path?: string[] } },
) {
  return proxyRequest(request, context);
}

export async function POST(
  request: NextRequest,
  context: { params?: { path?: string[] } },
) {
  return proxyRequest(request, context);
}

export async function PUT(
  request: NextRequest,
  context: { params?: { path?: string[] } },
) {
  return proxyRequest(request, context);
}

export async function PATCH(
  request: NextRequest,
  context: { params?: { path?: string[] } },
) {
  return proxyRequest(request, context);
}

export async function DELETE(
  request: NextRequest,
  context: { params?: { path?: string[] } },
) {
  return proxyRequest(request, context);
}

export async function OPTIONS(
  request: NextRequest,
  context: { params?: { path?: string[] } },
) {
  return proxyRequest(request, context);
}
