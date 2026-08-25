"use client";

import { useRouter } from "next/navigation";
import {
  type Dispatch,
  type SetStateAction,
  useCallback,
  useEffect,
  useRef,
  useState,
} from "react";

import { AppShell } from "@/components/app-shell";
import { CardChat } from "@/components/card-chat";
import { CardDocument } from "@/components/card-document";
import { StatusBadge } from "@/components/status-badge";
import { Alert, AlertError } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { useSession } from "@/hooks/use-session";
import { openAppealStream } from "@/lib/appeal-stream";
import { ApiError, fetchAppeal, fetchMessages, sendReply } from "@/lib/api";
import { asRecord, asText } from "@/lib/format";
import { OUTCOME_LABEL } from "@/lib/labels";
import { takeReturn } from "@/lib/return-path";
import type { AppealDetail, AppealMessage, StreamEvent } from "@/lib/types";

export function AppealWorkspace({ appealId }: { appealId: number }) {
  const login = useSession();
  const router = useRouter();
  const [appeal, setAppeal] = useState<AppealDetail | null>(null);
  const [messages, setMessages] = useState<AppealMessage[]>([]);
  const [pendingThought, setPendingThought] = useState("");
  const [pendingMessage, setPendingMessage] = useState("");
  const [runMark, setRunMark] = useState<{ outcome?: string } | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [missing, setMissing] = useState(false);
  const [runError, setRunError] = useState<string | null>(null);
  const seq = useRef(0);
  const closeRef = useRef<(() => void) | null>(null);
  const readyRef = useRef(false);
  const queueRef = useRef<StreamEvent[]>([]);

  const deliver = useCallback((event: StreamEvent) => {
    if (!readyRef.current) {
      queueRef.current.push(event);
      return;
    }
    applyEvent(
      event,
      setAppeal,
      setMessages,
      setPendingThought,
      setPendingMessage,
      setRunError,
      setRunMark,
      seq,
      () => {
        void refresh(appealId, setAppeal, setMessages);
      },
    );
  }, [appealId]);

  const attachStream = useCallback(() => {
    closeRef.current?.();
    closeRef.current = openAppealStream(appealId, deliver);
  }, [appealId, deliver]);

  useEffect(() => {
    if (!login) {
      return;
    }
    let cancelled = false;
    readyRef.current = false;
    queueRef.current = [];
    attachStream();
    void Promise.all([fetchAppeal(appealId), fetchMessages(appealId)])
      .then(([detail, feed]) => {
        if (cancelled) {
          return;
        }
        setAppeal(detail);
        setMessages(feed.items);
        readyRef.current = true;
        const queued = queueRef.current;
        queueRef.current = [];
        for (const event of queued) {
          deliver(event);
        }
        if (detail.run_status !== "running") {
          closeRef.current?.();
        }
      })
      .catch((err: unknown) => {
        if (err instanceof ApiError && err.status === 404) {
          setMissing(true);
          return;
        }
        setError(err instanceof Error ? err.message : "Ошибка");
      });
    return () => {
      cancelled = true;
      readyRef.current = false;
      closeRef.current?.();
    };
  }, [login, appealId, attachStream, deliver]);

  if (!login) {
    return (
      <main className="mx-auto max-w-[1280px] px-6 py-10">
        <p className="text-muted-foreground">Проверяем сессию…</p>
      </main>
    );
  }

  if (missing) {
    return (
      <AppShell login={login}>
        <AlertError>нет такого обращения</AlertError>
        <Button className="mt-4" variant="outline" onClick={() => router.push("/desk")}>
          На стол
        </Button>
      </AppShell>
    );
  }

  if (!appeal) {
    return (
      <AppShell login={login}>
        {error ? <AlertError>{error}</AlertError> : <Skeleton className="h-64" />}
      </AppShell>
    );
  }

  const decision = asRecord(appeal.card.decision);
  const running = appeal.run_status === "running";
  const outcome = asText(decision.outcome);

  return (
    <AppShell login={login} fill>
      <div className="flex min-h-0 flex-1 flex-col gap-3">
        <div className="flex shrink-0 items-center gap-3">
          <h1 className="font-serif text-xl">R-{appeal.id}</h1>
          <StatusBadge status={appeal.status} />
          {running ? <Badge>идёт разбор</Badge> : null}
          <span className="text-sm text-muted-foreground">
            {OUTCOME_LABEL[outcome ?? ""] ?? outcome ?? "исхода ещё нет"}
          </span>
          <span className="text-sm text-muted-foreground">
            {running ? "run: идёт" : "run: тихо"}
          </span>
          <Button className="ml-auto" variant="outline" size="sm" onClick={() => router.push(takeReturn())}>
            Назад
          </Button>
        </div>
        {runError ? <AlertError>{runError}</AlertError> : null}
        {error ? <Alert>{error}</Alert> : null}
        <div className="grid min-h-0 flex-1 grid-cols-2 gap-4">
          <CardDocument card={appeal.card} running={running} />
          <CardChat
            intake={asRecord(appeal.card.intake)}
            messages={foldTools(messages)}
            pendingThought={pendingThought}
            pendingMessage={pendingMessage}
            running={running}
            runMark={running ? null : runMark}
            onReply={async (text) => {
              setRunError(null);
              setRunMark(null);
              setPendingThought("");
              setPendingMessage("");
              await sendReply(appealId, text);
              setAppeal({ ...appeal, run_status: "running" });
              setMessages((current) => [
                ...current,
                {
                  id: --seq.current,
                  author: login,
                  kind: "dispatcher_reply",
                  body: { text },
                  created_at: new Date().toISOString(),
                },
              ]);
              attachStream();
            }}
          />
        </div>
      </div>
    </AppShell>
  );
}

function applyEvent(
  event: StreamEvent,
  setAppeal: Dispatch<SetStateAction<AppealDetail | null>>,
  setMessages: Dispatch<SetStateAction<AppealMessage[]>>,
  setPendingThought: Dispatch<SetStateAction<string>>,
  setPendingMessage: Dispatch<SetStateAction<string>>,
  setRunError: Dispatch<SetStateAction<string | null>>,
  setRunMark: Dispatch<SetStateAction<{ outcome?: string } | null>>,
  seq: { current: number },
  onFinished: () => void,
) {
  if (event.type === "card_updated") {
    setAppeal((current) =>
      current ? { ...current, card: asRecord(event.card), run_status: "running" } : current,
    );
    return;
  }
  if (event.type === "thought") {
    const delta = asText(event.delta);
    if (delta) {
      setPendingThought((current) => current + delta);
      return;
    }
    const text = asText(event.text);
    if (text) {
      flushThought(setPendingThought, setMessages, seq, text);
    }
    return;
  }
  if (event.type === "tool_call") {
    flushThought(setPendingThought, setMessages, seq);
    setMessages((current) => [...current, liveMessage(--seq.current, "tool_call", event)]);
    return;
  }
  if (event.type === "tool_result") {
    setMessages((current) => [...current, liveMessage(--seq.current, "tool_result", event)]);
    return;
  }
  if (event.type === "message_delta") {
    flushThought(setPendingThought, setMessages, seq);
    const delta = asText(event.delta) ?? "";
    if (delta) {
      setPendingMessage((current) => current + delta);
    }
    return;
  }
  if (event.type === "message_final") {
    const text = asText(event.text) ?? "";
    setPendingMessage("");
    if (text) {
      setMessages((current) => [...current, liveMessage(--seq.current, "message", { text })]);
    }
    return;
  }
  if (event.type === "run_finished") {
    flushThought(setPendingThought, setMessages, seq);
    setPendingMessage((text) => {
      if (text) {
        setMessages((current) => [...current, liveMessage(--seq.current, "message", { text })]);
      }
      return "";
    });
    setAppeal((current) =>
      current
        ? {
            ...current,
            run_status: "idle",
            status: (asText(event.status) as AppealDetail["status"]) || current.status,
            auto_in_prod: Boolean(event.auto_in_prod),
          }
        : current,
    );
    setRunMark({ outcome: asText(event.outcome) ?? undefined });
    onFinished();
    return;
  }
  if (event.type === "run_error") {
    setRunError(asText(event.detail) ?? "Прогон упал");
    setMessages((current) => [
      ...current,
      liveMessage(--seq.current, "run_error", { detail: asText(event.detail) }),
    ]);
    return;
  }
  if (event.type === "run_started" || event.type === "context_usage") {
    return;
  }
  setMessages((current) => [
    ...current,
    liveMessage(--seq.current, "unknown", { type: event.type }),
  ]);
}

function flushThought(
  setPendingThought: Dispatch<SetStateAction<string>>,
  setMessages: Dispatch<SetStateAction<AppealMessage[]>>,
  seq: { current: number },
  forced?: string,
) {
  setPendingThought((current) => {
    const text = forced ?? current;
    if (text.trim()) {
      setMessages((messages) => [...messages, liveMessage(--seq.current, "thought", { text })]);
    }
    return "";
  });
}

function liveMessage(
  id: number,
  kind: string,
  body: Record<string, unknown>,
): AppealMessage {
  return {
    id,
    author: "agent",
    kind,
    body,
    created_at: new Date().toISOString(),
  };
}

function foldTools(messages: AppealMessage[]): AppealMessage[] {
  const source = messages.some((item) => item.id < 0)
    ? messages
    : [...messages].sort((left, right) => left.id - right.id);
  const out: AppealMessage[] = [];
  const indexByKey = new Map<string, number>();

  function remember(body: Record<string, unknown>, index: number, fallback: string) {
    const ident = asText(body.id);
    if (ident) {
      indexByKey.set(ident, index);
    }
    const name = asText(body.name);
    if (name) {
      indexByKey.set(`${name}:${fallback}`, index);
    }
  }

  function findPair(body: Record<string, unknown>, kind: string): number | undefined {
    const ident = asText(body.id);
    if (ident && indexByKey.has(ident)) {
      const index = indexByKey.get(ident);
      if (index !== undefined && out[index].kind === kind) {
        return index;
      }
    }
    const name = asText(body.name);
    if (!name) {
      return undefined;
    }
    for (let i = out.length - 1; i >= 0; i -= 1) {
      if (out[i].kind === kind && asText(asRecord(out[i].body).name) === name) {
        return i;
      }
    }
    return undefined;
  }

  for (const message of source) {
    const body = asRecord(message.body);
    if (message.kind === "tool_call" || message.kind === "tool_result") {
      const other = message.kind === "tool_call" ? "tool_result" : "tool_call";
      const index = findPair(body, other);
      if (index !== undefined) {
        out[index] = {
          ...out[index],
          kind: "tool_result",
          body: { ...out[index].body, ...body },
        };
        remember(body, index, "pair");
        continue;
      }
      remember(body, out.length, "open");
      out.push(message);
      continue;
    }
    out.push(message);
  }
  return out;
}

async function refresh(
  id: number,
  setAppeal: Dispatch<SetStateAction<AppealDetail | null>>,
  setMessages: Dispatch<SetStateAction<AppealMessage[]>>,
) {
  const [detail, feed] = await Promise.all([fetchAppeal(id), fetchMessages(id)]);
  setAppeal(detail);
  setMessages(feed.items);
}
