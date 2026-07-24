import { config } from "../config";

export type Role = "analyst" | "reviewer" | "approver" | "admin";

export type ApiOptions = {
  role: Role;
  userId?: string;
  userName?: string;
};

async function request<T>(
  path: string,
  options: ApiOptions,
  init: RequestInit = {},
): Promise<T> {
  const headers = new Headers(init.headers || {});
  headers.set("x-user-id", options.userId || "ui-user");
  headers.set("x-user-name", options.userName || "UI User");
  headers.set("x-user-role", options.role);
  if (init.body && !(init.body instanceof FormData) && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }
  const res = await fetch(`${config.apiBaseUrl}${path}`, { ...init, headers });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`${res.status}: ${text}`);
  }
  if (res.status === 204) return undefined as T;
  return (await res.json()) as T;
}

export const api = {
  health: (opts: ApiOptions) => request<{ status: string; environment: string }>("/api/health", opts),
  listAgents: (opts: ApiOptions) =>
    request<Array<{ id: string; name: string; description: string }>>("/api/catalog/agents", opts),
  listWorkspaces: (opts: ApiOptions) =>
    request<Array<{ id: string; name: string; description: string }>>("/api/workspaces", opts),
  createWorkspace: (opts: ApiOptions, body: { name: string; description?: string }) =>
    request<{ id: string; name: string }>("/api/workspaces", opts, {
      method: "POST",
      body: JSON.stringify(body),
    }),
  listFiles: (opts: ApiOptions, workspaceId: string) =>
    request<Array<{ id: string; filename: string; size: number }>>(
      `/api/workspaces/${workspaceId}/files`,
      opts,
    ),
  uploadFile: async (opts: ApiOptions, workspaceId: string, file: File) => {
    const form = new FormData();
    form.append("upload", file);
    return request<{ id: string; filename: string }>(
      `/api/workspaces/${workspaceId}/files`,
      opts,
      { method: "POST", body: form },
    );
  },
  runAgent: (
    opts: ApiOptions,
    workspaceId: string,
    body: { agent_id: string; input_file_ids: string[] },
  ) =>
    request<{
      id: string;
      status: string;
      result: Record<string, unknown>;
      output_file_ids: string[];
      error?: string;
    }>(`/api/workspaces/${workspaceId}/agents/runs`, opts, {
      method: "POST",
      body: JSON.stringify(body),
    }),
  listAudit: (opts: ApiOptions, workspaceId: string) =>
    request<Array<{ id: string; action: string; actor: string; created_at: string; details: Record<string, unknown> }>>(
      `/api/workspaces/${workspaceId}/audit`,
      opts,
    ),
};
