import type { AppealStatus, Channel, DeskStatus } from "@/lib/types";

export const STATUS_LABEL: Record<AppealStatus, string> = {
  new: "Новые",
  clarify: "Нужно уточнение",
  dispatch: "Диспетчеру",
  approve: "На согласовании",
  done: "Разобрано",
};

export const DESK_ORDER: DeskStatus[] = ["new", "clarify", "dispatch", "approve"];

export const CHANNEL_LABEL: Record<Channel, string> = {
  email: "email",
  telegram: "Telegram",
  call: "звонок",
  lk: "личный кабинет",
};

export const OUTCOME_LABEL: Record<string, string> = {
  create: "Создать заявку",
  update: "Обновить заявку",
  clarify: "Нужно уточнение",
  dispatch: "Диспетчеру",
  approve: "На согласовании",
  refuse_auto: "Отказ автоматики",
};

export const BINDING_LABEL: Record<string, string> = {
  empty: "не извлечено",
  mentioned: "упомянуто",
  resolved: "опознано",
  not_found: "не найдено",
  ambiguous: "несколько",
};

export const FACT_LABEL: Record<string, string> = {
  customer: "Клиент",
  site: "Объект",
  asset: "Оборудование",
  problem: "Проблема",
  symptoms: "Симптомы",
  desired_deadline: "Желаемый срок",
  backup: "Резерв",
  history: "Прошлое",
};

export const KIND_LABEL: Record<string, string> = {
  fact: "факт",
  assumption: "предположение",
  system: "система",
};
