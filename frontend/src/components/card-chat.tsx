"use client";

import { type FormEvent, useState } from "react";

import { AgentMarkdown } from "@/components/agent-markdown";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { asRecord, asText } from "@/lib/format";
import type { AppealMessage } from "@/lib/types";

export function CardChat({
  messages,
  running,
  onReply,
}: {
  messages: AppealMessage[];
  running: boolean;
  onReply: (text: string) => Promise<void>;
}) {
  const [text, setText] = useState("");
  const [pending, setPending] = useState(false);

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

  return (
    <Card className="flex min-h-[32rem] flex-col">
      <CardHeader>
        <CardTitle>Диалог</CardTitle>
      </CardHeader>
      <CardContent className="flex flex-1 flex-col gap-4">
        <div className="flex flex-1 flex-col gap-2 overflow-y-auto">
          {messages.length === 0 ? (
            <p className="text-sm text-muted-foreground">
              {running ? "агент разбирает обращение…" : "лента пуста"}
            </p>
          ) : (
            messages.map((message) => (
              <ChatItem key={message.id} message={message} running={running} />
            ))
          )}
        </div>
        <form className="flex flex-col gap-2" onSubmit={(event) => void onSubmit(event)}>
          <label htmlFor="reply" className="text-sm font-medium">
            Реплика диспетчера
          </label>
          <Textarea
            id="reply"
            value={text}
            onChange={(event) => setText(event.target.value)}
            disabled={running || pending}
          />
          <Button type="submit" disabled={running || pending || text.trim().length === 0}>
            Отправить
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}

function ChatItem({
  message,
  running,
}: {
  message: AppealMessage;
  running: boolean;
}) {
  const body = asRecord(message.body);
  if (message.kind === "thought" || message.kind === "tool_call" || message.kind === "tool_result") {
    return (
      <CompactBlock
        title={titleOf(message, body)}
        text={bodyText(message, body)}
        running={running}
      />
    );
  }
  const text = asText(body.text) ?? "";
  return (
    <div className="rounded-md border border-border px-3 py-2">
      <div className="text-xs text-muted-foreground">
        {message.author === "agent" ? "агент" : message.author}
      </div>
      {message.kind === "message" || message.author === "agent" ? (
        <AgentMarkdown text={text} />
      ) : (
        <p className="text-sm whitespace-pre-wrap">{text}</p>
      )}
    </div>
  );
}

function CompactBlock({
  title,
  text,
  running,
}: {
  title: string;
  text: string;
  running: boolean;
}) {
  return (
    <details className="rounded-md border border-border px-3 py-2 text-sm" open={running}>
      <summary className="cursor-pointer text-muted-foreground">{title}</summary>
      <pre className="mt-2 overflow-x-auto whitespace-pre-wrap text-xs">{text}</pre>
    </details>
  );
}

function titleOf(message: AppealMessage, body: Record<string, unknown>): string {
  if (message.kind === "thought") {
    return "мысль";
  }
  const name = asText(body.name) ?? "тул";
  return message.kind === "tool_call" ? `тул ${name}` : `${name}: ${asText(body.summary) ?? "ответ"}`;
}

function bodyText(message: AppealMessage, body: Record<string, unknown>): string {
  if (message.kind === "thought") {
    return asText(body.text) ?? "";
  }
  return JSON.stringify(body, null, 2);
}
