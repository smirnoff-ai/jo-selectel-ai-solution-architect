"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { type Dispatch, type SetStateAction, useEffect, useRef, useState } from "react";

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
import { takeReturn } from "@/lib/return-path";
import type { AppealDetail, AppealMessage, StreamEvent } from "@/lib/types";

export function AppealWorkspace({ appealId }: { appealId: number }) {
  const login = useSession();
  const router = useRouter();
  const [appeal, setAppeal] = useState<AppealDetail | null>(null);
  const [messages, setMessages] = useState<AppealMessage[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [missing, setMissing] = useState(false);
  const [runError, setRunError] = useState<string | null>(null);
  const seq = useRef(0);
  const closeRef = useRef<(() => void) | null>(null);

  useEffect(() => {
    if (!login) {
      return;
    }
    let cancelled = false;
    void Promise.all([fetchAppeal(appealId), fetchMessages(appealId)])
      .then(([detail, feed]) => {
        if (cancelled) {
          return;
        }
        setAppeal(detail);
        setMessages(feed.items);
        if (detail.run_status === "running") {
          closeRef.current = openAppealStream(appealId, (event) =>
            applyEvent(event, setAppeal, setMessages, setRunError, seq, () => {
              void refresh(appealId, setAppeal, setMessages);
            }),
          );
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
      closeRef.current?.();
    };
  }, [login, appealId]);

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
        <Link href="/desk" className="mt-4 text-sm text-primary underline">
          На стол
        </Link>
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

  return (
    <AppShell login={login}>
      <div className="flex items-start justify-between gap-4">
        <div className="flex flex-col gap-2">
          <div className="flex items-center gap-3">
            <h1 className="font-serif text-3xl">R-{appeal.id}</h1>
            <StatusBadge status={appeal.status} />
            {running ? <Badge>идёт разбор</Badge> : null}
          </div>
          <p className="text-sm text-muted-foreground">
            создал {appeal.created_by} ·{" "}
            {appeal.auto_in_prod || decision.auto_in_prod
              ? "в проде ушло бы автоматом"
              : "в проде нужен человек"}
          </p>
        </div>
        <Button variant="outline" onClick={() => router.push(takeReturn())}>
          Назад
        </Button>
      </div>
      {runError ? <AlertError className="mt-4">{runError}</AlertError> : null}
      {error ? <Alert className="mt-4">{error}</Alert> : null}
      <div className="mt-6 grid grid-cols-2 gap-6">
        <CardDocument card={appeal.card} running={running} />
        <CardChat
          messages={messages}
          running={running}
          onReply={async (text) => {
            setRunError(null);
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
            closeRef.current?.();
            closeRef.current = openAppealStream(appealId, (event) =>
              applyEvent(event, setAppeal, setMessages, setRunError, seq, () => {
                void refresh(appealId, setAppeal, setMessages);
              }),
            );
          }}
        />
      </div>
    </AppShell>
  );
}

function applyEvent(
  event: StreamEvent,
  setAppeal: Dispatch<SetStateAction<AppealDetail | null>>,
  setMessages: Dispatch<SetStateAction<AppealMessage[]>>,
  setRunError: Dispatch<SetStateAction<string | null>>,
  seq: { current: number },
  onFinished: () => void,
) {
  if (event.type === "card_updated") {
    setAppeal((current) =>
      current ? { ...current, card: asRecord(event.card) } : current,
    );
    return;
  }
  if (event.type === "run_finished") {
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
    onFinished();
    return;
  }
  if (event.type === "run_error") {
    setRunError(asText(event.detail) ?? "Прогон упал");
    return;
  }
  const mapped = messageFromEvent(event, --seq.current);
  if (mapped) {
    setMessages((current) => [...current, mapped]);
  }
}

function messageFromEvent(event: StreamEvent, id: number): AppealMessage | null {
  if (event.type === "thought") {
    return {
      id,
      author: "agent",
      kind: "thought",
      body: { text: event.text },
      created_at: new Date().toISOString(),
    };
  }
  if (event.type === "tool_call" || event.type === "tool_result") {
    return {
      id,
      author: "agent",
      kind: event.type,
      body: event,
      created_at: new Date().toISOString(),
    };
  }
  if (event.type === "message_final") {
    return {
      id,
      author: "agent",
      kind: "message",
      body: { text: event.text },
      created_at: new Date().toISOString(),
    };
  }
  return null;
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
