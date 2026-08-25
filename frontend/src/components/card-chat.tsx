"use client";

import { type FormEvent, useEffect, useRef, useState } from "react";

import { AgentMarkdown } from "@/components/agent-markdown";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Field, FieldLabel } from "@/components/ui/field";
import { Textarea } from "@/components/ui/textarea";
import { asRecord, asText, formatDateTime } from "@/lib/format";
import { CHANNEL_LABEL, TOOL_LABEL } from "@/lib/labels";
import type { AppealMessage, Channel } from "@/lib/types";
import { cn } from "@/lib/utils";

export function CardChat({
  intake,
  messages,
  pendingThought,
  pendingMessage,
  running,
  runMark,
  onReply,
}: {
  intake: Record<string, unknown>;
  messages: AppealMessage[];
  pendingThought: string;
  pendingMessage: string;
  running: boolean;
  runMark: { outcome?: string } | null;
  onReply: (text: string) => Promise<void>;
}) {
  const [text, setText] = useState("");
  const [pending, setPending] = useState(false);
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ block: "end" });
  }, [messages, pendingThought, pendingMessage]);

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    const value = text.trim();
    if (!value || pending || running) {
      return;
    }
    setPending(true);
    try {
      await onReply(value);
      setText("");
    } finally {
      setPending(false);
    }
  }

  const channel = asText(intake.channel) as Channel | null;

  return (
    <div className="flex min-h-0 flex-1 flex-col overflow-hidden rounded-xl border border-border bg-card">
      <div className="min-h-0 flex-1 overflow-y-auto px-4 py-3">
        <div className="flex flex-col gap-2.5">
          <div className="rounded-lg bg-muted/40 px-3 py-2.5">
            <div className="text-[11px] tracking-wide text-muted-foreground uppercase">
              {channel ? CHANNEL_LABEL[channel] : "вход"}
              {asText(intake.sender) ? ` · ${asText(intake.sender)}` : ""}
              {asText(intake.received_at) ? ` · ${formatDateTime(asText(intake.received_at))}` : ""}
            </div>
            <p className="mt-1.5 text-sm leading-relaxed whitespace-pre-wrap">
              {asText(intake.text) ?? "—"}
            </p>
            {asText(intake.attachment_text) ? (
              <p className="mt-1 text-xs text-muted-foreground whitespace-pre-wrap">
                вложение: {asText(intake.attachment_text)}
              </p>
            ) : null}
          </div>
          {messages.map((message) => (
            <ChatItem key={message.id} message={message} />
          ))}
          {pendingThought ? <ThoughtBlock text={pendingThought} live /> : null}
          {pendingMessage ? <AnswerBlock text={pendingMessage} live /> : null}
          {running && !pendingThought && !pendingMessage ? <Cursor /> : null}
          {runMark ? (
            <p className="py-2 text-center text-[11px] tracking-wide text-muted-foreground uppercase">
              прогон закончен
              {runMark.outcome ? ` · ${runMark.outcome}` : ""}
            </p>
          ) : null}
          <div ref={endRef} />
        </div>
      </div>
      <form
        className="flex shrink-0 flex-col gap-2 border-t border-border bg-muted/20 px-4 py-3"
        onSubmit={(event) => void onSubmit(event)}
      >
        <Field>
          <FieldLabel htmlFor="reply">Реплика диспетчера</FieldLabel>
          <Textarea
            id="reply"
            value={text}
            onChange={(event) => setText(event.target.value)}
            disabled={running || pending}
            className="min-h-20"
          />
        </Field>
        <Button type="submit" disabled={running || pending || text.trim().length === 0}>
          Отправить
        </Button>
      </form>
    </div>
  );
}

function ChatItem({ message }: { message: AppealMessage }) {
  const body = asRecord(message.body);
  if (message.kind === "thought") {
    return <ThoughtBlock text={asText(body.text) ?? ""} />;
  }
  if (message.kind === "tool_call" || message.kind === "tool_result") {
    return <ToolCard body={body} live={message.kind === "tool_call" && !asText(body.summary)} />;
  }
  if (message.kind === "run_error") {
    return (
      <div className="rounded-lg border border-destructive/40 bg-destructive/10 px-3 py-2 text-sm text-destructive">
        {asText(body.detail) ?? asText(body.text) ?? "Прогон упал"}
      </div>
    );
  }
  if (message.kind === "unknown") {
    return (
      <div className="px-1 text-xs text-muted-foreground">{asText(body.type) ?? "событие"}</div>
    );
  }
  const text = asText(body.text) ?? "";
  if (message.author === "agent") {
    return <AnswerBlock text={text} />;
  }
  return (
    <div className="rounded-lg bg-primary/10 px-3 py-2.5">
      <div className="text-[11px] tracking-wide text-muted-foreground uppercase">{message.author}</div>
      <p className="mt-1 text-sm whitespace-pre-wrap">{text}</p>
    </div>
  );
}

function ThoughtBlock({ text, live = false }: { text: string; live?: boolean }) {
  return (
    <details className="px-1" open={live}>
      <summary className="cursor-pointer text-[11px] tracking-[0.14em] text-muted-foreground uppercase">
        <span className="inline-flex items-center gap-2">
          {live ? (
            <span className="inline-flex gap-0.5" aria-hidden>
              <span className="size-1 animate-pulse rounded-full bg-primary" />
              <span className="size-1 animate-pulse rounded-full bg-primary [animation-delay:150ms]" />
            </span>
          ) : null}
          думаю
        </span>
      </summary>
      <p className="mt-2 font-mono text-xs leading-relaxed text-muted-foreground italic whitespace-pre-wrap">
        {text}
        {live ? <Cursor /> : null}
      </p>
    </details>
  );
}

function AnswerBlock({ text, live = false }: { text: string; live?: boolean }) {
  return (
    <div className="rounded-lg bg-muted/35 px-3 py-2.5">
      <div className="text-[11px] tracking-wide text-muted-foreground uppercase">агент</div>
      <AgentMarkdown text={text} />
      {live ? <Cursor /> : null}
    </div>
  );
}

function ToolCard({ body, live }: { body: Record<string, unknown>; live: boolean }) {
  const name = asText(body.name) ?? "тул";
  const status = asText(body.status);
  const summary = asText(body.summary);
  const args = body.args ?? asRecord(body).args;
  const result = body.result;
  const failed = status === "error";
  return (
    <div
      className={cn(
        "rounded-r-lg border-l-2 px-3 py-2",
        failed ? "border-destructive bg-destructive/10" : "border-primary/50 bg-muted/25",
      )}
    >
      <div className="flex flex-wrap items-center gap-2">
        <span className="font-mono text-[11px] text-muted-foreground">{name}</span>
        <span className="text-sm">{TOOL_LABEL[name] ?? name}</span>
        <Badge variant="outline">
          {failed ? "ошибка" : live ? "вызывается" : "ок"}
        </Badge>
      </div>
      {summary ? <p className="mt-1 text-sm">{summary}</p> : null}
      {args !== undefined ? (
        <details className="mt-1.5">
          <summary className="cursor-pointer text-[11px] text-muted-foreground">параметры</summary>
          <pre className="mt-1 overflow-x-auto font-mono text-[11px] text-muted-foreground whitespace-pre-wrap">
            {JSON.stringify(args, null, 2)}
          </pre>
        </details>
      ) : null}
      {result !== undefined ? (
        <details className="mt-1">
          <summary className="cursor-pointer text-[11px] text-muted-foreground">ответ</summary>
          <pre className="mt-1 overflow-x-auto font-mono text-[11px] text-muted-foreground whitespace-pre-wrap">
            {JSON.stringify(result, null, 2)}
          </pre>
        </details>
      ) : null}
    </div>
  );
}

function Cursor() {
  return (
    <span
      className={cn("ml-0.5 inline-block w-2 animate-pulse text-primary")}
      aria-hidden
    >
      |
    </span>
  );
}
