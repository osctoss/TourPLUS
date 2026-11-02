/**
 * Centralized API Client for TourPlus AI
 * Strictly typed, handles session cookies, standardized error formats.
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000/api/v1";

export interface ApiResponse<T = any> {
  data: T;
  status: number;
}

export interface ApiError {
  message: string;
  errors?: Record<string, string[]>;
  status: number;
}

async function request<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint.startsWith("/") ? "" : "/"}${endpoint}`;
  
  const headers = new Headers(options.headers);
  if (!headers.has("Content-Type") && !(options.body instanceof FormData)) {
    headers.set("Content-Type", "application/json");
  }
  headers.set("Accept", "application/json");

  const config: RequestInit = {
    ...options,
    headers,
    credentials: "include", // For session cookie sharing with Django backend
  };

  try {
    const response = await fetch(url, config);

    if (response.status === 204) {
      return {} as T;
    }

    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
      const error: ApiError = {
        message: data.detail || data.message || "An unexpected error occurred.",
        errors: typeof data === "object" ? data : undefined,
        status: response.status,
      };
      throw error;
    }

    return data as T;
  } catch (err: any) {
    if (err.status) {
      throw err;
    }
    throw {
      message: err.message || "Network error. Please verify backend server is reachable.",
      status: 0,
    } as ApiError;
  }
}

export const apiClient = {
  get: <T>(endpoint: string, options?: RequestInit) =>
    request<T>(endpoint, { ...options, method: "GET" }),

  post: <T>(endpoint: string, body?: any, options?: RequestInit) =>
    request<T>(endpoint, {
      ...options,
      method: "POST",
      body: body instanceof FormData ? body : JSON.stringify(body),
    }),

  patch: <T>(endpoint: string, body?: any, options?: RequestInit) =>
    request<T>(endpoint, {
      ...options,
      method: "PATCH",
      body: body instanceof FormData ? body : JSON.stringify(body),
    }),

  delete: <T>(endpoint: string, options?: RequestInit) =>
    request<T>(endpoint, { ...options, method: "DELETE" }),
};

