import type { StreamEvent } from "@/lib/types";

export function openAppealStream(
  id: number,
  onEvent: (event: StreamEvent) => void,
): () => void {
  const controller = new AbortController();
  void readFrames(id, onEvent, controller.signal);
  return () => controller.abort();
}

async function readFrames(
  id: number,
  onEvent: (event: StreamEvent) => void,
  signal: AbortSignal,
): Promise<void> {
  try {
    const response = await fetch(`/api/v1/appeals/${id}/stream`, {
      signal,
      cache: "no-store",
      headers: { Accept: "text/event-stream" },
    });
    if (!response.ok || !response.body) {
      onEvent({ type: "run_error", detail: `stream ${response.status}` });
      return;
    }
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";
    while (true) {
      const { done, value } = await reader.read();
      if (done) {
        break;
      }
      buffer += decoder.decode(value, { stream: true }).replace(/\r\n/g, "\n");
      const frames = buffer.split("\n\n");
      buffer = frames.pop() ?? "";
      for (const frame of frames) {
        const event = parseBlock(frame);
        if (event) {
          onEvent(event);
        }
      }
    }
  } catch (err) {
    if (signal.aborted) {
      return;
    }
    onEvent({
      type: "run_error",
      detail: err instanceof Error ? err.message : "stream",
    });
  }
}

function parseBlock(block: string): StreamEvent | null {
  let type = "message";
  const data: string[] = [];
  for (const line of block.split("\n")) {
    if (line.startsWith("event:")) {
      type = line.slice(6).trim();
    }
    if (line.startsWith("data:")) {
      data.push(line.slice(5).trimStart());
    }
  }
  if (data.length === 0) {
    return null;
  }
  try {
    const payload = JSON.parse(data.join("\n")) as Record<string, unknown>;
    return { ...payload, type: typeof payload.type === "string" ? payload.type : type };
  } catch {
    return { type, raw: data.join("\n") };
  }
}
