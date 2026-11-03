import type { ApiEnvelope } from '../types';

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? '/api/v1';

export class ApiError extends Error {
  readonly status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
  }
}

function buildQuery(params?: Record<string, unknown>): string {
  if (!params) return '';
  const search = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value === undefined || value === null || value === '') return;
    search.append(key, String(value));
  });
  const query = search.toString();
  return query ? `?${query}` : '';
}

async function request<T>(
  path: string,
  options: RequestInit & { params?: Record<string, unknown> } = {},
): Promise<T> {
  const { params, headers, ...rest } = options;
  const response = await fetch(`${API_BASE}${path}${buildQuery(params)}`, {
    ...rest,
    headers: {
      'Content-Type': 'application/json',
      ...(headers ?? {}),
    },
  });

  if (!response.ok) {
    let message = `Error ${response.status}`;
    try {
      const body = await response.json();
      if (body?.message) message = body.message;
    } catch {
      // respuesta sin cuerpo JSON
    }
    throw new ApiError(message, response.status);
  }

  return (await response.json()) as T;
}

export async function get<T>(
  path: string,
  params?: Record<string, unknown>,
): Promise<ApiEnvelope<T>> {
  return request<ApiEnvelope<T>>(path, { method: 'GET', params });
}

export async function post<T>(path: string, body?: unknown): Promise<ApiEnvelope<T>> {
  return request<ApiEnvelope<T>>(path, {
    method: 'POST',
    body: body === undefined ? undefined : JSON.stringify(body),
  });
}

export async function put<T>(path: string, body?: unknown): Promise<ApiEnvelope<T>> {
  return request<ApiEnvelope<T>>(path, {
    method: 'PUT',
    body: body === undefined ? undefined : JSON.stringify(body),
  });
}

export async function remove<T>(path: string, params?: Record<string, unknown>): Promise<ApiEnvelope<T>> {
  return request<ApiEnvelope<T>>(path, { method: 'DELETE', params });
}

export async function downloadCsv(path: string, params?: Record<string, unknown>): Promise<void> {
  const response = await fetch(`${API_BASE}${path}${buildQuery(params)}`);
  if (!response.ok) {
    throw new ApiError(`No se pudo exportar el CSV (${response.status})`, response.status);
  }
  const blob = await response.blob();
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = 'gastos.csv';
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}
