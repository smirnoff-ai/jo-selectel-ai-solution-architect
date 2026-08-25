"use client";

import { useRouter } from "next/navigation";
import { type FormEvent, useState } from "react";

import { AppShell } from "@/components/app-shell";
import { AlertError } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Field, FieldError, FieldGroup, FieldLabel } from "@/components/ui/field";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { useSession } from "@/hooks/use-session";
import { createAppeal } from "@/lib/api";
import { localDateTimeInput, localInputToIso } from "@/lib/format";
import { CHANNEL_LABEL } from "@/lib/labels";
import type { Channel } from "@/lib/types";

const CHANNELS: Channel[] = ["email", "telegram", "call", "lk"];

export function AppealCreateForm() {
  const login = useSession();
  const router = useRouter();
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [textError, setTextError] = useState<string | null>(null);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const text = String(form.get("text") ?? "").trim();
    const received = String(form.get("received_at") ?? "");
    if (!text) {
      setTextError("Введите текст обращения");
      return;
    }
    if (!received || pending) {
      return;
    }
    setPending(true);
    setError(null);
    setTextError(null);
    try {
      const created = await createAppeal({
        channel: String(form.get("channel")),
        sender: String(form.get("sender") ?? "").trim() || null,
        received_at: localInputToIso(received),
        text,
        attachment_text: String(form.get("attachment_text") ?? "").trim() || null,
      });
      router.push(`/appeals/${created.id}`);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Не удалось создать");
      setPending(false);
    }
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
      <h1 className="font-serif text-3xl">Новое обращение</h1>
      <form className="mt-6 max-w-xl" onSubmit={(event) => void onSubmit(event)}>
        <FieldGroup>
          <Field>
            <FieldLabel htmlFor="channel">Канал</FieldLabel>
            <select
              id="channel"
              name="channel"
              required
              defaultValue="email"
              className="h-9 rounded-md border border-input bg-card px-2 text-sm"
            >
              {CHANNELS.map((value) => (
                <option key={value} value={value}>
                  {CHANNEL_LABEL[value]}
                </option>
              ))}
            </select>
          </Field>
          <Field>
            <FieldLabel htmlFor="sender">Отправитель</FieldLabel>
            <Input id="sender" name="sender" placeholder="Андрей, СеверФуд" />
          </Field>
          <Field>
            <FieldLabel htmlFor="received_at">Получено</FieldLabel>
            <Input
              id="received_at"
              name="received_at"
              type="datetime-local"
              required
              defaultValue={localDateTimeInput()}
            />
          </Field>
          <Field data-invalid={Boolean(textError)}>
            <FieldLabel htmlFor="text">Текст</FieldLabel>
            <Textarea id="text" name="text" required aria-invalid={Boolean(textError)} />
            {textError ? <FieldError>{textError}</FieldError> : null}
          </Field>
          <Field>
            <FieldLabel htmlFor="attachment_text">Текст вложения</FieldLabel>
            <Textarea id="attachment_text" name="attachment_text" />
          </Field>
        </FieldGroup>
        {error ? <AlertError className="mt-4">{error}</AlertError> : null}
        <div className="mt-6 flex gap-2">
          <Button type="submit" disabled={pending}>
            Создать
          </Button>
          <Button type="button" variant="outline" onClick={() => router.push("/desk")}>
            Отмена
          </Button>
        </div>
      </form>
    </AppShell>
  );
}
