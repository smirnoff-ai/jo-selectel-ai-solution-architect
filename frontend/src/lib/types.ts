export type Channel = "email" | "telegram" | "call" | "lk";
export type DeskStatus = "new" | "clarify" | "dispatch" | "approve";
export type AppealStatus = DeskStatus | "done";
export type RunStatus = "idle" | "running";

export type DeskRow = {
  id: number;
  received_at: string;
  channel: Channel;
  sender: string | null;
  text_preview: string;
  run_status: RunStatus;
};

export type JournalRow = DeskRow & {
  status: AppealStatus;
  created_by: string;
};

export type DeskWidget = {
  status: DeskStatus;
  count: number;
  recent: DeskRow[];
};

export type AppealDetail = {
  id: number;
  status: AppealStatus;
  run_status: RunStatus;
  created_by: string;
  auto_in_prod: boolean;
  card: Record<string, unknown>;
};

export type AppealMessage = {
  id: number;
  author: string;
  kind: string;
  body: Record<string, unknown>;
  created_at: string;
};

export type StreamEvent = {
  type: string;
} & Record<string, unknown>;
