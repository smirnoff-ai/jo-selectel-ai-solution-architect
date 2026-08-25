"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { AppShell } from "@/components/app-shell";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Empty } from "@/components/ui/empty";
import { Skeleton } from "@/components/ui/skeleton";
import { AlertError } from "@/components/ui/alert";
import { useSession } from "@/hooks/use-session";
import { fetchDesk } from "@/lib/api";
import { formatDateTime } from "@/lib/format";
import { CHANNEL_LABEL, DESK_ORDER, STATUS_LABEL } from "@/lib/labels";
import { rememberReturn } from "@/lib/return-path";
import type { DeskWidget } from "@/lib/types";

export function DeskBoard() {
  const login = useSession();
  const router = useRouter();
  const [widgets, setWidgets] = useState<DeskWidget[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!login) {
      return;
    }
    rememberReturn("/desk");
    void fetchDesk()
      .then((data) => setWidgets(data.widgets))
      .catch((err: unknown) => setError(err instanceof Error ? err.message : "Ошибка"));
  }, [login]);

  if (!login) {
    return (
      <main className="mx-auto max-w-[1280px] px-6 py-10">
        <p className="text-muted-foreground">Проверяем сессию…</p>
      </main>
    );
  }

  return (
    <AppShell login={login}>
      <div className="flex items-center justify-between gap-4">
        <h1 className="font-serif text-3xl">Стол</h1>
        <Button onClick={() => router.push("/appeals/new")}>Создать обращение</Button>
      </div>
      {error ? <AlertError className="mt-6">{error}</AlertError> : null}
      <div className="mt-6 grid grid-cols-2 gap-4">
        {widgets
          ? DESK_ORDER.map((status) => {
              const widget = widgets.find((item) => item.status === status);
              return (
                <WidgetCard
                  key={status}
                  status={status}
                  count={widget?.count ?? 0}
                  recent={widget?.recent ?? []}
                />
              );
            })
          : Array.from({ length: 4 }, (_, index) => (
              <Skeleton key={index} className="h-48" />
            ))}
      </div>
    </AppShell>
  );
}

function WidgetCard({
  status,
  count,
  recent,
}: {
  status: DeskWidget["status"];
  count: number;
  recent: DeskWidget["recent"];
}) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>
          <Link
            href={`/journal?status=${status}`}
            className="hover:text-primary focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
            onClick={() => rememberReturn(`/journal?status=${status}`)}
          >
            {STATUS_LABEL[status]}
          </Link>
          <span className="ml-2 font-sans text-sm text-muted-foreground">{count}</span>
        </CardTitle>
      </CardHeader>
      <CardContent>
        {recent.length === 0 ? (
          <Empty>нет обращений</Empty>
        ) : (
          <ul className="flex flex-col gap-2">
            {recent.map((row) => (
              <li key={row.id}>
                <Link
                  href={`/appeals/${row.id}`}
                  className="flex flex-col gap-0.5 rounded-md px-1 py-1 hover:bg-muted focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                  onClick={() => rememberReturn("/desk")}
                >
                  <span className="flex items-center gap-2 text-xs text-muted-foreground">
                    <span>{formatDateTime(row.received_at)}</span>
                    <span>{CHANNEL_LABEL[row.channel]}</span>
                    {row.run_status === "running" ? (
                      <span className="text-primary">идёт разбор</span>
                    ) : null}
                  </span>
                  <span className="text-sm">{row.sender || "отправитель не указан"}</span>
                  <span className="truncate text-sm text-muted-foreground">
                    {row.text_preview}
                  </span>
                </Link>
              </li>
            ))}
          </ul>
        )}
      </CardContent>
    </Card>
  );
}
