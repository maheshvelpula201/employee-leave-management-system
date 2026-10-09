import { apiRequest } from "./api";

export type AuthUser = {
  user_id: number;
  name: string;
  email: string;
  role: string;
  company_id: number;
  is_active: boolean;
};

export type LoginResponse = {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: AuthUser;
};

export type LoginCredentials = {
  role: string;
  email: string;
  password: string;
};

const ACCESS_TOKEN_KEY = "hr_access_token";
const REFRESH_TOKEN_KEY = "hr_refresh_token";
const USER_KEY = "hr_user";

export async function login(
  credentials: LoginCredentials,
): Promise<LoginResponse> {
  const response = await apiRequest<LoginResponse>("/auth/login", {
    method: "POST",
    body: credentials,
  });

  sessionStorage.setItem(ACCESS_TOKEN_KEY, response.access_token);
  sessionStorage.setItem(REFRESH_TOKEN_KEY, response.refresh_token);
  sessionStorage.setItem(USER_KEY, JSON.stringify(response.user));

  return response;
}

export function getAccessToken(): string | null {
  return sessionStorage.getItem(ACCESS_TOKEN_KEY);
}

export function getRefreshToken(): string | null {
  return sessionStorage.getItem(REFRESH_TOKEN_KEY);
}

export function getCurrentUser(): AuthUser | null {
  const value = sessionStorage.getItem(USER_KEY);

  if (!value) {
    return null;
  }

  try {
    return JSON.parse(value) as AuthUser;
  } catch {
    return null;
  }
}

export function logoutLocal(): void {
  sessionStorage.removeItem(ACCESS_TOKEN_KEY);
  sessionStorage.removeItem(REFRESH_TOKEN_KEY);
  sessionStorage.removeItem(USER_KEY);
}
