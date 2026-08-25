import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { asRecord, asText, formatDateTime } from "@/lib/format";
import {
  BINDING_LABEL,
  CHANNEL_LABEL,
  FACT_LABEL,
  KIND_LABEL,
  OUTCOME_LABEL,
} from "@/lib/labels";
import type { Channel } from "@/lib/types";

const FACT_KEYS = [
  "customer",
  "site",
  "asset",
  "problem",
  "symptoms",
  "desired_deadline",
  "backup",
  "history",
] as const;

export function CardDocument({
  card,
  running,
}: {
  card: Record<string, unknown>;
  running: boolean;
}) {
  const intake = asRecord(card.intake);
  const facts = asRecord(card.facts);
  const contract = asRecord(card.contract);
  const calculation = asRecord(card.calculation);
  const decision = asRecord(card.decision);
  const channel = asText(intake.channel) as Channel | null;

  return (
    <div className="flex flex-col gap-4">
      {running ? (
        <p className="text-sm text-primary">идёт разбор — блоки наполняются по шагам</p>
      ) : null}
      <Card>
        <CardHeader>
          <CardTitle>Вход</CardTitle>
        </CardHeader>
        <CardContent className="flex flex-col gap-2 text-sm">
          <Row label="Канал" value={channel ? CHANNEL_LABEL[channel] : "—"} />
          <Row label="Отправитель" value={asText(intake.sender) ?? "не указан"} />
          <Row label="Получено" value={formatDateTime(asText(intake.received_at))} />
          <Row label="Текст" value={asText(intake.text) ?? "—"} />
          <Row
            label="Вложение"
            value={asText(intake.attachment_text) ?? "вложения нет"}
          />
        </CardContent>
      </Card>
      <Card>
        <CardHeader>
          <CardTitle>Факты</CardTitle>
        </CardHeader>
        <CardContent className="flex flex-col gap-3">
          {FACT_KEYS.map((key) => (
            <FactRow key={key} name={key} slot={asRecord(facts[key])} />
          ))}
        </CardContent>
      </Card>
      <Card>
        <CardHeader>
          <CardTitle>Ответы систем</CardTitle>
        </CardHeader>
        <CardContent className="flex flex-col gap-3 text-sm">
          <SystemBlock title="Клиент и объект" facts={facts} />
          <Separator />
          <BindingBlock title="Оборудование" slot={asRecord(facts.asset)} />
          <Separator />
          <ContractBlock contract={contract} />
          <Separator />
          <BindingBlock title="Открытые заявки" slot={asRecord(facts.history)} />
        </CardContent>
      </Card>
      <Card>
        <CardHeader>
          <CardTitle>Решение</CardTitle>
        </CardHeader>
        <CardContent className="flex flex-col gap-2 text-sm">
          <Row
            label="Исход"
            value={OUTCOME_LABEL[asText(decision.outcome) ?? ""] ?? asText(decision.outcome) ?? "ещё нет"}
          />
          <Row label="Почему" value={asText(decision.reason) ?? "—"} />
          <List label="Вопросы" items={asStringList(decision.questions)} />
          <WarningList items={decision.warnings} />
        </CardContent>
      </Card>
      <Card>
        <CardHeader>
          <CardTitle>Расчёт</CardTitle>
        </CardHeader>
        <CardContent className="flex flex-col gap-3">
          <Metric title="Приоритет" metric={asRecord(calculation.priority)} valueKey="value" />
          <Metric title="SLA" metric={asRecord(calculation.sla)} valueKey="code" />
          <Deadline metric={asRecord(calculation.deadline)} />
        </CardContent>
      </Card>
      <Card>
        <CardHeader>
          <CardTitle>Результат</CardTitle>
        </CardHeader>
        <CardContent className="flex flex-col gap-3 text-sm">
          <TicketDraft draft={asRecord(decision.ticket_draft)} />
          <DryRun run={asRecord(decision.itsm_dry_run)} />
          {asText(decision.reply_draft) ? (
            <Row label="Черновик ответа" value={asText(decision.reply_draft) ?? ""} />
          ) : null}
        </CardContent>
      </Card>
    </div>
  );
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <div className="text-xs text-muted-foreground">{label}</div>
      <div className="whitespace-pre-wrap">{value}</div>
    </div>
  );
}

function FactRow({ name, slot }: { name: string; slot: Record<string, unknown> }) {
  const binding = asRecord(slot.binding);
  const mention = asText(slot.mention) ?? asText(slot.value);
  const status = asText(binding.status);
  const label = asText(binding.label) ?? asText(binding.id);
  const evidence = firstEvidence(slot.evidences);
  return (
    <div className="flex flex-col gap-1 border-b border-border pb-3 last:border-0 last:pb-0">
      <div className="flex items-center gap-2">
        <span className="text-sm font-medium">{FACT_LABEL[name]}</span>
        {status ? <Badge variant="outline">{BINDING_LABEL[status] ?? status}</Badge> : null}
      </div>
      <p className="text-sm">{label || mention || "не извлечено"}</p>
      {evidence ? (
        <p className="text-xs text-muted-foreground">
          {KIND_LABEL[evidence.kind] ?? evidence.kind}
          {evidence.fragment ? ` · «${evidence.fragment}»` : ""}
          {evidence.confidence ? ` · ${evidence.confidence}` : ""}
        </p>
      ) : null}
    </div>
  );
}

function SystemBlock({
  title,
  facts,
}: {
  title: string;
  facts: Record<string, unknown>;
}) {
  return (
    <div className="flex flex-col gap-2">
      <BindingBlock title={title} slot={asRecord(facts.customer)} />
      <BindingBlock title="Площадка" slot={asRecord(facts.site)} />
    </div>
  );
}

function BindingBlock({ title, slot }: { title: string; slot: Record<string, unknown> }) {
  const binding = asRecord(slot.binding);
  const candidates = Array.isArray(binding.candidates) ? binding.candidates : [];
  return (
    <div>
      <div className="text-xs text-muted-foreground">{title}</div>
      <div>
        {asText(binding.label) || asText(binding.id) || BINDING_LABEL[asText(binding.status) ?? ""] || "—"}
      </div>
      {candidates.length > 0 ? (
        <ul className="mt-1 list-disc pl-5 text-muted-foreground">
          {candidates.map((item, index) => {
            const row = asRecord(item);
            return (
              <li key={`${asText(row.id) ?? index}`}>
                {asText(row.label) || asText(row.id) || JSON.stringify(item)}
              </li>
            );
          })}
        </ul>
      ) : null}
    </div>
  );
}

function ContractBlock({ contract }: { contract: Record<string, unknown> }) {
  const status = asText(contract.status);
  if (status === "empty" || !status) {
    return (
      <div>
        <div className="text-xs text-muted-foreground">Договор</div>
        <div>нет площадки — договор не запрашивали</div>
      </div>
    );
  }
  return (
    <div>
      <div className="text-xs text-muted-foreground">Договор</div>
      <div>
        {asText(contract.id)} · {asText(contract.plan) ?? "без плана"} ·{" "}
        {asText(contract.response_sla) ?? "без SLA"}
      </div>
    </div>
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
  const missing = asStringList(metric.missing);
  return (
    <div className="flex flex-col gap-1 text-sm">
      <div className="text-xs text-muted-foreground">{title}</div>
      <div>{asText(metric[valueKey]) ?? "нет"}</div>
      {asText(metric.formula) ? (
        <div className="text-muted-foreground">{asText(metric.formula)}</div>
      ) : null}
      {missing.length > 0 ? (
        <div className="text-muted-foreground">не хватает: {missing.join(", ")}</div>
      ) : null}
    </div>
  );
}

function Deadline({ metric }: { metric: Record<string, unknown> }) {
  return (
    <Metric
      title="Дедлайн"
      metric={{ ...metric, value: formatDateTime(asText(metric.at)) }}
      valueKey="value"
    />
  );
}

function TicketDraft({ draft }: { draft: Record<string, unknown> }) {
  if (!asText(draft.customer_id) && !asText(draft.summary)) {
    return <div>собрать заявку некуда</div>;
  }
  return (
    <div>
      <div className="text-xs text-muted-foreground">Проект заявки</div>
      <div>
        {asText(draft.customer_id)} / {asText(draft.site_id)} / {asText(draft.asset_id) ?? "без актива"}
      </div>
      <div>{asText(draft.summary)}</div>
      <div>приоритет {asText(draft.priority)}</div>
    </div>
  );
}

function DryRun({ run }: { run: Record<string, unknown> }) {
  if (!Object.keys(run).length) {
    return null;
  }
  return (
    <div>
      <div className="text-xs text-muted-foreground">Примерка ITSM</div>
      <div>
        accepted: {String(run.accepted)} · persisted: {String(run.persisted)} · id:{" "}
        {asText(run.would_ticket_id) ?? asText(run.ticket_id) ?? "—"}
      </div>
    </div>
  );
}

function List({ label, items }: { label: string; items: string[] }) {
  if (items.length === 0) {
    return null;
  }
  return (
    <div>
      <div className="text-xs text-muted-foreground">{label}</div>
      <ul className="list-disc pl-5">
        {items.map((item) => (
          <li key={item}>{item}</li>
        ))}
      </ul>
    </div>
  );
}

function WarningList({ items }: { items: unknown }) {
  const rows = Array.isArray(items) ? items : [];
  if (rows.length === 0) {
    return null;
  }
  return (
    <div>
      <div className="text-xs text-muted-foreground">Предупреждения</div>
      <ul className="list-disc pl-5">
        {rows.map((item, index) => {
          const row = asRecord(item);
          return <li key={index}>{asText(row.text) ?? String(item)}</li>;
        })}
      </ul>
    </div>
  );
}

function firstEvidence(value: unknown): {
  kind: string;
  fragment: string | null;
  confidence: string | null;
} | null {
  if (!Array.isArray(value) || value.length === 0) {
    return null;
  }
  const row = asRecord(value[0]);
  return {
    kind: asText(row.kind) ?? "",
    fragment: asText(row.fragment),
    confidence: asText(row.confidence),
  };
}

function asStringList(value: unknown): string[] {
  if (!Array.isArray(value)) {
    return [];
  }
  return value.filter((item): item is string => typeof item === "string");
}
