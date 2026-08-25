import { Badge } from "@/components/ui/badge";
import { STATUS_LABEL } from "@/lib/labels";
import type { AppealStatus } from "@/lib/types";

const VARIANT: Record<AppealStatus, "default" | "secondary" | "outline" | "warning"> = {
  new: "default",
  clarify: "outline",
  dispatch: "secondary",
  approve: "warning",
  done: "secondary",
};

export function StatusBadge({ status }: { status: AppealStatus }) {
  return <Badge variant={VARIANT[status]}>{STATUS_LABEL[status]}</Badge>;
}
