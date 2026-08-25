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

export const SOURCE_LABEL: Record<string, string> = {
  intake_text: "текст входа",
  intake_sender: "отправитель",
  intake_attachment: "вложение",
  dispatcher: "диспетчер",
  crm: "CRM",
  eam: "EAM",
  contract: "договор",
  itsm: "ITSM",
};

export const CONFIDENCE_LABEL: Record<string, string> = {
  high: "высокая",
  medium: "средняя",
  low: "низкая",
};

export const TOOL_LABEL: Record<string, string> = {
  patch_facts: "Запись фактов",
  update_card: "Запись карточки",
  search_sites: "Поиск площадок (CRM)",
  search_assets: "Поиск оборудования (EAM)",
  search_tickets: "Открытые заявки (ITSM)",
  get_contract: "Договор площадки",
  calculate: "Расчёт срока и приоритета",
};
