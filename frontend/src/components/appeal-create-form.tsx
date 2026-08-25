"use client";

import { useRouter } from "next/navigation";
import { type FormEvent, useState } from "react";

import { AppShell } from "@/components/app-shell";
import { AlertError } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import {
  Field,
  FieldDescription,
  FieldError,
  FieldGroup,
  FieldLabel,
} from "@/components/ui/field";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { useSession } from "@/hooks/use-session";
import { createAppeal } from "@/lib/api";
import { localDateTimeInput, localInputToIso } from "@/lib/format";
import { INTAKE_PRESETS, PRESET_RECEIVED_AT, type IntakePreset } from "@/lib/intake-presets";
import { CHANNEL_LABEL } from "@/lib/labels";
import type { Channel } from "@/lib/types";

const CHANNELS: Channel[] = ["email", "telegram", "call", "lk"];

export function AppealCreateForm() {
  const login = useSession();
  const router = useRouter();
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [textError, setTextError] = useState<string | null>(null);
  const [channel, setChannel] = useState<Channel>("email");
  const [sender, setSender] = useState("");
  const [receivedAt, setReceivedAt] = useState(() => localDateTimeInput());
  const [text, setText] = useState("");
  const [attachmentText, setAttachmentText] = useState("");
  const [activePreset, setActivePreset] = useState<IntakePreset["id"] | null>(null);

  function applyPreset(preset: IntakePreset) {
    setChannel(preset.channel);
    setSender(preset.sender);
    setReceivedAt(localDateTimeInput(new Date(PRESET_RECEIVED_AT)));
    setText(preset.text);
    setAttachmentText("");
    setActivePreset(preset.id);
    setTextError(null);
  }

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const trimmed = text.trim();
    if (!trimmed) {
      setTextError("Введите текст обращения");
      return;
    }
    if (!receivedAt || pending) {
      return;
    }
    setPending(true);
    setError(null);
    setTextError(null);
    try {
      const created = await createAppeal({
        channel,
        sender: sender.trim() || null,
        received_at: localInputToIso(receivedAt),
        text: trimmed,
        attachment_text: attachmentText.trim() || null,
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
            <FieldLabel>Сценарии</FieldLabel>
            <FieldDescription>
              Подставить канал, отправителя, время демо и текст из пакета S1–S4
            </FieldDescription>
            <div className="flex flex-wrap gap-2">
              {INTAKE_PRESETS.map((preset) => (
                <Button
                  key={preset.id}
                  type="button"
                  size="sm"
                  variant={activePreset === preset.id ? "default" : "outline"}
                  aria-pressed={activePreset === preset.id}
                  onClick={() => applyPreset(preset)}
                >
                  {preset.id}. {preset.title}
                </Button>
              ))}
            </div>
          </Field>
          <Field>
            <FieldLabel htmlFor="channel">Канал</FieldLabel>
            <select
              id="channel"
              name="channel"
              required
              value={channel}
              onChange={(event) => {
                setChannel(event.target.value as Channel);
                setActivePreset(null);
              }}
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
            <Input
              id="sender"
              name="sender"
              placeholder="Андрей, СеверФуд"
              value={sender}
              onChange={(event) => {
                setSender(event.target.value);
                setActivePreset(null);
              }}
            />
          </Field>
          <Field>
            <FieldLabel htmlFor="received_at">Получено</FieldLabel>
            <Input
              id="received_at"
              name="received_at"
              type="datetime-local"
              required
              value={receivedAt}
              onChange={(event) => {
                setReceivedAt(event.target.value);
                setActivePreset(null);
              }}
            />
          </Field>
          <Field data-invalid={Boolean(textError)}>
            <FieldLabel htmlFor="text">Текст</FieldLabel>
            <Textarea
              id="text"
              name="text"
              required
              aria-invalid={Boolean(textError)}
              value={text}
              onChange={(event) => {
                setText(event.target.value);
                setActivePreset(null);
              }}
            />
            {textError ? <FieldError>{textError}</FieldError> : null}
          </Field>
          <Field>
            <FieldLabel htmlFor="attachment_text">Текст вложения</FieldLabel>
            <Textarea
              id="attachment_text"
              name="attachment_text"
              value={attachmentText}
              onChange={(event) => {
                setAttachmentText(event.target.value);
                setActivePreset(null);
              }}
            />
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
