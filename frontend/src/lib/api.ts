import type {
  AppealDetail,
  AppealMessage,
  DeskWidget,
  JournalRow,
} from "@/lib/types";

export class ApiError extends Error {
  constructor(
    readonly status: number,
    message: string,
  ) {
    super(message);
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(path, {
    credentials: "same-origin",
    ...init,
  });
  if (response.status === 204) {
    return undefined as T;
  }
  if (!response.ok) {
    let detail = "Ошибка запроса";
    try {
      const body = (await response.json()) as { detail?: unknown };
      if (typeof body.detail === "string") {
        detail = body.detail;
      }
    } catch {
      detail = response.statusText || detail;
    }
    throw new ApiError(response.status, detail);
  }
  return (await response.json()) as T;
}

export function fetchMe() {
  return request<{ login: string }>("/api/v1/auth/me");
}

export function login(body: { login: string; password: string }) {
  return request<{ login: string }>("/api/v1/auth/login", {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(body),
  });
}

export function logout() {
  return request<void>("/api/v1/auth/logout", { method: "POST" });
}

export function fetchDesk() {
  return request<{ widgets: DeskWidget[] }>("/api/v1/appeals/desk");
}

export function fetchJournal(query: URLSearchParams) {
  const suffix = query.toString();
  return request<{ items: JournalRow[] }>(
    `/api/v1/appeals${suffix ? `?${suffix}` : ""}`,
  );
}

export function createAppeal(body: {
  channel: string;
  sender: string | null;
  received_at: string;
  text: string;
  attachment_text: string | null;
}) {
  return request<{ id: number; status: string; run_status: string }>(
    "/api/v1/appeals",
    {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify(body),
    },
  );
}

export function fetchAppeal(id: number) {
  return request<AppealDetail>(`/api/v1/appeals/${id}`);
}

export function fetchMessages(id: number) {
  return request<{ items: AppealMessage[] }>(`/api/v1/appeals/${id}/messages`);
}

export function sendReply(id: number, text: string) {
  return request<{ id: number; run_status: string }>(
    `/api/v1/appeals/${id}/replies`,
    {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ text }),
    },
  );
}
