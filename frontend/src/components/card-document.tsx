"use client";

import { type ReactNode, useState } from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { asRecord, asText, formatDateTime } from "@/lib/format";
import {
  BINDING_LABEL,
  CHANNEL_LABEL,
  CONFIDENCE_LABEL,
  FACT_LABEL,
  KIND_LABEL,
  OUTCOME_LABEL,
  SOURCE_LABEL,
} from "@/lib/labels";
import type { Channel } from "@/lib/types";
import { cn } from "@/lib/utils";

const IDENTITY = ["customer", "site", "asset", "history"] as const;
const NARRATIVE = ["problem", "symptoms", "desired_deadline", "backup"] as const;

export function CardDocument({
  card,
  running,
}: {
  card: Record<string, unknown>;
  running: boolean;
}) {
  const [mode, setMode] = useState<"form" | "json">("form");
  const intake = asRecord(card.intake);
  const facts = asRecord(card.facts);
  const contract = asRecord(card.contract);
  const calculation = asRecord(card.calculation);
  const decision = asRecord(card.decision);
  const channel = asText(intake.channel) as Channel | null;

  return (
    <div className="flex min-h-0 flex-1 flex-col overflow-hidden rounded-xl border border-border bg-card">
      <div className="flex shrink-0 items-center gap-2 border-b border-border px-4 py-2.5">
        <Button
          size="sm"
          variant={mode === "form" ? "default" : "ghost"}
          aria-pressed={mode === "form"}
          onClick={() => setMode("form")}
        >
          Форма
        </Button>
        <Button
          size="sm"
          variant={mode === "json" ? "default" : "ghost"}
          aria-pressed={mode === "json"}
          onClick={() => setMode("json")}
        >
          JSON
        </Button>
        {running ? <span className="ml-auto text-xs text-primary">слоты обновляются</span> : null}
      </div>
      <div className="min-h-0 flex-1 overflow-y-auto px-4 py-3">
        {mode === "json" ? (
          <pre className="font-mono text-xs whitespace-pre-wrap text-muted-foreground">
            {JSON.stringify(card, null, 2)}
          </pre>
        ) : (
          <div className="flex flex-col">
            <Section title="Вход">
              <Row label="Канал" value={channel ? CHANNEL_LABEL[channel] : "—"} />
              <Row label="Отправитель" value={asText(intake.sender) ?? "не указан"} />
              <Row label="Получено" value={formatDateTime(asText(intake.received_at))} />
              <Row label="Текст" value={asText(intake.text) ?? "—"} />
              <Row
                label="Вложение"
                value={asText(intake.attachment_text) ?? "вложения нет"}
              />
            </Section>
            <Section title="Факты">
              {IDENTITY.map((key) => (
                <IdentitySlot key={key} name={key} slot={asRecord(facts[key])} />
              ))}
              {NARRATIVE.map((key) => (
                <NarrativeSlot key={key} name={key} slot={asRecord(facts[key])} />
              ))}
            </Section>
            <ContractCard contract={contract} />
            <CalculationCard calculation={calculation} />
            <DecisionCard decision={decision} />
          </div>
        )}
      </div>
    </div>
  );
}

function Section({ title, children }: { title: string; children: ReactNode }) {
  return (
    <section className="flex flex-col gap-3 border-b border-border py-4 last:border-0">
      <h2 className="text-[11px] font-medium tracking-[0.16em] text-muted-foreground uppercase">
        {title}
      </h2>
      {children}
    </section>
  );
}

function IdentitySlot({ name, slot }: { name: string; slot: Record<string, unknown> }) {
  const binding = asRecord(slot.binding);
  const status = asText(binding.status) ?? "empty";
  const mention = asText(slot.mention);
  const candidates = Array.isArray(binding.candidates) ? binding.candidates : [];
  return (
    <div className="flex flex-col gap-1 rounded-md bg-muted/25 px-3 py-2.5">
      <div className="flex items-center gap-2">
        <Led status={status} />
        <span className="text-sm font-medium">{FACT_LABEL[name]}</span>
        <Badge variant="outline">{BINDING_LABEL[status] ?? status}</Badge>
      </div>
      {status === "empty" ? <p className="text-sm text-muted-foreground">не извлечено</p> : null}
      {mention ? <p className="text-sm text-muted-foreground">в тексте: {mention}</p> : null}
      {status === "resolved" ? (
        <p className="text-sm">
          <span className="font-mono">{asText(binding.id)}</span>
          {asText(binding.label) ? ` · ${asText(binding.label)}` : ""}
        </p>
      ) : null}
      {status === "not_found" ? (
        <p className="text-sm text-destructive">в реестре нет</p>
      ) : null}
      {status === "ambiguous" && candidates.length > 0 ? (
        <ul className="flex flex-col gap-1 text-sm">
          {candidates.map((item, index) => {
            const row = asRecord(item);
            return (
              <li key={`${asText(row.id) ?? index}`}>
                <span className="font-mono">{asText(row.id)}</span>
                {asText(row.label) ? ` · ${asText(row.label)}` : ""}
                {asText(row.site_id) ? ` · площадка ${asText(row.site_id)}` : ""}
              </li>
            );
          })}
        </ul>
      ) : null}
      <EvidenceList items={slot.evidences} />
    </div>
  );
}

function NarrativeSlot({ name, slot }: { name: string; slot: Record<string, unknown> }) {
  const value = asText(slot.value);
  const parsed = asText(slot.parsed_at);
  return (
    <div className="flex flex-col gap-1 px-1">
      <span className="text-sm font-medium">{FACT_LABEL[name]}</span>
      <p className="text-sm">{value ?? "не извлечено"}</p>
      {parsed ? (
        <p className="text-xs text-muted-foreground">разобрано: {formatDateTime(parsed)}</p>
      ) : null}
      <EvidenceList items={slot.evidences} />
    </div>
  );
}

function EvidenceList({ items }: { items: unknown }) {
  if (!Array.isArray(items) || items.length === 0) {
    return null;
  }
  return (
    <ul className="flex flex-col gap-1 text-xs text-muted-foreground">
      {items.map((item, index) => {
        const row = asRecord(item);
        const kind = asText(row.kind) ?? "";
        const source = asText(row.source) ?? "";
        const confidence = asText(row.confidence) ?? "";
        const record = asRecord(row.record);
        const parts = [
          KIND_LABEL[kind] ?? kind,
          SOURCE_LABEL[source] ?? source,
          CONFIDENCE_LABEL[confidence] ?? confidence,
        ].filter(Boolean);
        return (
          <li key={index}>
            {parts.join(" · ")}
            {kind === "fact" && asText(row.fragment) ? ` · «${asText(row.fragment)}»` : ""}
            {kind === "system" && asText(record.id)
              ? ` · ${asText(record.system) ?? source} · ${asText(record.id)}${asText(record.label) ? ` · ${asText(record.label)}` : ""}`
              : ""}
          </li>
        );
      })}
    </ul>
  );
}

function ContractCard({ contract }: { contract: Record<string, unknown> }) {
  const status = asText(contract.status) ?? "empty";
  const coverage = Array.isArray(contract.coverage)
    ? contract.coverage.filter((item): item is string => typeof item === "string")
    : [];
  return (
    <Section title="Договор">
      {status === "empty" ? <p className="text-sm text-muted-foreground">не запрашивали</p> : null}
      {status === "not_found" ? (
        <p className="text-sm text-destructive">договора на площадку нет</p>
      ) : null}
      {status === "resolved" ? (
        <div className="flex flex-col gap-2 text-sm">
          <Row label="Id" value={asText(contract.id) ?? "—"} mono />
          <Row label="План" value={asText(contract.plan) ?? "—"} />
          <Row label="SLA ответа" value={asText(contract.response_sla) ?? "—"} />
          <Row label="Окно" value={asText(contract.service_window) ?? "—"} />
          <Row label="Площадка" value={asText(contract.site_id) ?? "—"} mono />
          <Row label="Покрытие" value={coverage.length ? coverage.join(", ") : "—"} />
        </div>
      ) : null}
    </Section>
  );
}

function CalculationCard({ calculation }: { calculation: Record<string, unknown> }) {
  const status = asText(calculation.status);
  const branch = asText(calculation.branch);
  return (
    <Section title="Расчёт">
      <div className="flex flex-col gap-3 text-sm">
        <Row
          label="Статус"
          value={
            status === "blocked"
              ? "заблокирован"
              : status === "conditional"
                ? "условный"
                : status === "computed"
                  ? "посчитан"
                  : status ?? "—"
          }
        />
        <Row
          label="Ветка"
          value={branch === "create" ? "создать" : branch === "update" ? "обновить" : "нет"}
        />
        <Metric title="Приоритет" metric={asRecord(calculation.priority)} valueKey="value" />
        <Metric title="SLA" metric={asRecord(calculation.sla)} valueKey="code" />
        <Metric
          title="Дедлайн"
          metric={{
            ...asRecord(calculation.deadline),
            value: formatDateTime(asText(asRecord(calculation.deadline).at)),
          }}
          valueKey="value"
        />
      </div>
    </Section>
  );
}

function DecisionCard({ decision }: { decision: Record<string, unknown> }) {
  const outcome = asText(decision.outcome);
  const grounds = Array.isArray(decision.grounds)
    ? decision.grounds.filter((item): item is string => typeof item === "string")
    : [];
  const questions = Array.isArray(decision.questions) ? decision.questions : [];
  const warnings = Array.isArray(decision.warnings) ? decision.warnings : [];
  const draft = asRecord(decision.ticket_draft);
  const dry = asRecord(decision.itsm_dry_run);
  const auto = decision.auto_in_prod;
  return (
    <Section title="Решение">
      <div className="flex flex-col gap-2 text-sm">
        <div className="flex items-center gap-2">
          <span className="text-xs text-muted-foreground">Исход</span>
          <Badge variant="outline">{OUTCOME_LABEL[outcome ?? ""] ?? outcome ?? "ещё нет"}</Badge>
        </div>
        {asText(decision.reason) ? <Row label="Почему" value={asText(decision.reason) ?? ""} /> : null}
        {grounds.length > 0 ? <Row label="Опоры" value={grounds.join(", ")} /> : null}
        {questions.length > 0 ? (
          <div>
            <div className="text-xs text-muted-foreground">Вопросы</div>
            <ul className="flex flex-col gap-1">
              {questions.map((item, index) => {
                const row = asRecord(item);
                return <li key={index}>{asText(row.text) ?? String(item)}</li>;
              })}
            </ul>
          </div>
        ) : null}
        {warnings.length > 0 ? (
          <div className="rounded-md border border-warning px-3 py-2">
            {warnings.map((item, index) => {
              const row = asRecord(item);
              return (
                <p key={index}>
                  {asText(row.code) ? `${asText(row.code)} · ` : ""}
                  {asText(row.text) ?? String(item)}
                </p>
              );
            })}
          </div>
        ) : null}
        {asText(decision.reply_draft) ? (
          <Row label="Черновик ответа" value={asText(decision.reply_draft) ?? ""} />
        ) : null}
        {outcome === "create" || outcome === "update" ? (
          <div>
            <div className="text-xs text-muted-foreground">Проект заявки</div>
            <p>
              {asText(draft.customer_id)} / {asText(draft.site_id)} /{" "}
              {asText(draft.asset_id) ?? "без актива"}
            </p>
            <p>{asText(draft.summary)}</p>
          </div>
        ) : null}
        {Object.keys(dry).length > 0 ? (
          <Row
            label="Примерка ITSM"
            value={`accepted ${String(dry.accepted)} · id ${asText(dry.would_ticket_id) ?? asText(dry.ticket_id) ?? "—"} · persisted ${String(dry.persisted)}`}
          />
        ) : null}
        <Row
          label="В проде автоматом"
          value={auto === true ? "да" : auto === false ? "нет" : "ещё нет"}
        />
      </div>
    </Section>
  );
}

function Metric({
  title,
  metric,
  valueKey,
}: {
  title: string;
  metric: Record<string, unknown>;
  valueKey: string;
}) {
  const missing = Array.isArray(metric.missing)
    ? metric.missing.filter((item): item is string => typeof item === "string")
    : [];
  const args = asRecord(metric.arguments);
  return (
    <div className="flex flex-col gap-1">
      <div className="text-xs text-muted-foreground">{title}</div>
      <div>{asText(metric[valueKey]) ?? "нет"}</div>
      {asText(metric.formula) ? (
        <div className="text-muted-foreground">{asText(metric.formula)}</div>
      ) : null}
      {Object.keys(args).length > 0 ? (
        <div className="text-xs text-muted-foreground">
          {Object.entries(args)
            .map(([key, value]) => `${key}=${String(value)}`)
            .join(" · ")}
        </div>
      ) : null}
      {missing.length > 0 ? (
        <div className="text-muted-foreground">не хватает: {missing.join(", ")}</div>
      ) : null}
    </div>
  );
}

function Row({
  label,
  value,
  mono = false,
}: {
  label: string;
  value: string;
  mono?: boolean;
}) {
  return (
    <div>
      <div className="text-xs text-muted-foreground">{label}</div>
      <div className={cn("whitespace-pre-wrap", mono && "font-mono")}>{value}</div>
    </div>
  );
}

function Led({ status }: { status: string }) {
  return (
    <span
      aria-hidden
      className={cn(
        "size-2 shrink-0 rounded-full",
        status === "resolved" && "bg-primary",
        status === "mentioned" && "animate-pulse bg-primary/50",
        status === "not_found" && "bg-destructive",
        status === "ambiguous" && "bg-warning",
        status === "empty" && "bg-muted-foreground/40",
      )}
    />
  );
}
