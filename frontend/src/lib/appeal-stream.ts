import type { StreamEvent } from "@/lib/types";

const TYPES = [
  "run_started",
  "thought",
  "tool_call",
  "tool_result",
  "card_updated",
  "message_delta",
  "message_final",
  "run_finished",
  "run_error",
] as const;

export function openAppealStream(
  id: number,
  onEvent: (event: StreamEvent) => void,
): () => void {
  const source = new EventSource(`/api/v1/appeals/${id}/stream`);
  for (const type of TYPES) {
    source.addEventListener(type, (raw) => {
      const frame = raw as MessageEvent<string>;
      try {
        const data = JSON.parse(frame.data) as Record<string, unknown>;
        onEvent({ ...data, type });
      } catch {
        onEvent({ type, raw: frame.data });
      }
    });
  }
  return () => source.close();
}
