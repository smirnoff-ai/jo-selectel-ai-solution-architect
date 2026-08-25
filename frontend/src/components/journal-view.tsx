"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { type FormEvent, useEffect, useState } from "react";

import { AppShell } from "@/components/app-shell";
import { StatusBadge } from "@/components/status-badge";
import { AlertError } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Empty } from "@/components/ui/empty";
import { Field, FieldGroup, FieldLabel } from "@/components/ui/field";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { useSession } from "@/hooks/use-session";
import { fetchJournal } from "@/lib/api";
import { formatDateTime } from "@/lib/format";
import { CHANNEL_LABEL, STATUS_LABEL } from "@/lib/labels";
import { rememberReturn } from "@/lib/return-path";
import type { AppealStatus, Channel, JournalRow } from "@/lib/types";

const STATUSES: Array<"all" | AppealStatus> = [
  "all",
  "new",
  "clarify",
  "dispatch",
  "approve",
  "done",
];
const CHANNELS: Array<"all" | Channel> = ["all", "email", "telegram", "call", "lk"];

export function JournalView() {
  const login = useSession();
  const params = useSearchParams();
  const router = useRouter();
  const [items, setItems] = useState<JournalRow[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  const status = params.get("status") ?? "all";
  const channel = params.get("channel") ?? "all";
  const receivedFrom = params.get("received_from") ?? "";
  const receivedTo = params.get("received_to") ?? "";

  useEffect(() => {
    if (!login) {
      return;
    }
    const query = new URLSearchParams();
    if (status !== "all") query.set("status", status);
    if (channel !== "all") query.set("channel", channel);
    if (receivedFrom) query.set("received_from", receivedFrom);
    if (receivedTo) query.set("received_to", receivedTo);
    rememberReturn(`/journal${query.toString() ? `?${query}` : ""}`);
    void fetchJournal(query)
      .then((data) => setItems(data.items))
      .catch((err: unknown) => setError(err instanceof Error ? err.message : "Ошибка"));
  }, [login, status, channel, receivedFrom, receivedTo]);

  function onFilter(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const next = new URLSearchParams();
    for (const key of ["status", "channel", "received_from", "received_to"]) {
      const value = String(form.get(key) ?? "");
      if (value && value !== "all") {
        next.set(key, value);
      }
    }
    router.push(`/journal${next.toString() ? `?${next}` : ""}`);
  }

  if (!login) {
    return (
      <main className="mx-auto max-w-[1280px] px-6 py-10">
        <p className="text-muted-foreground">Проверяем сессию…</p>
      </main>
    );
  }

  return (
    <AppShell login={login}>
      <h1 className="font-serif text-3xl">Журнал</h1>
      <form className="mt-6" onSubmit={onFilter}>
        <FieldGroup className="flex-row flex-wrap items-end">
          <Field>
            <FieldLabel htmlFor="status">Статус</FieldLabel>
            <select
              id="status"
              name="status"
              defaultValue={status}
              className="h-9 rounded-md border border-input bg-card px-2 text-sm"
            >
              {STATUSES.map((value) => (
                <option key={value} value={value}>
                  {value === "all" ? "все" : STATUS_LABEL[value]}
                </option>
              ))}
            </select>
          </Field>
          <Field>
            <FieldLabel htmlFor="channel">Канал</FieldLabel>
            <select
              id="channel"
              name="channel"
              defaultValue={channel}
              className="h-9 rounded-md border border-input bg-card px-2 text-sm"
            >
              {CHANNELS.map((value) => (
                <option key={value} value={value}>
                  {value === "all" ? "все" : CHANNEL_LABEL[value]}
                </option>
              ))}
            </select>
          </Field>
          <Field>
            <FieldLabel htmlFor="received_from">С</FieldLabel>
            <Input id="received_from" name="received_from" type="date" defaultValue={receivedFrom} />
          </Field>
          <Field>
            <FieldLabel htmlFor="received_to">По</FieldLabel>
            <Input id="received_to" name="received_to" type="date" defaultValue={receivedTo} />
          </Field>
          <Button type="submit" variant="outline">
            Применить
          </Button>
          <Button type="button" variant="ghost" onClick={() => router.push("/journal")}>
            Сброс
          </Button>
        </FieldGroup>
      </form>
      {error ? <AlertError className="mt-4">{error}</AlertError> : null}
      <div className="mt-6">
        {items === null ? (
          <div className="flex flex-col gap-2">
            <Skeleton className="h-10" />
            <Skeleton className="h-10" />
            <Skeleton className="h-10" />
          </div>
        ) : items.length === 0 ? (
          <Empty>нет обращений по фильтру</Empty>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Получено</TableHead>
                <TableHead>Канал</TableHead>
                <TableHead>Отправитель</TableHead>
                <TableHead>Текст</TableHead>
                <TableHead>Статус</TableHead>
                <TableHead>Кто создал</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {items.map((row) => (
                <TableRow
                  key={row.id}
                  tabIndex={0}
                  className="cursor-pointer focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                  onClick={() => router.push(`/appeals/${row.id}`)}
                  onKeyDown={(event) => {
                    if (event.key === "Enter" || event.key === " ") {
                      event.preventDefault();
                      router.push(`/appeals/${row.id}`);
                    }
                  }}
                >
                  <TableCell>{formatDateTime(row.received_at)}</TableCell>
                  <TableCell>{CHANNEL_LABEL[row.channel]}</TableCell>
                  <TableCell>{row.sender || "не указан"}</TableCell>
                  <TableCell className="max-w-xs truncate">{row.text_preview}</TableCell>
                  <TableCell>
                    <StatusBadge status={row.status} />
                  </TableCell>
                  <TableCell>{row.created_by}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </div>
    </AppShell>
  );
}
