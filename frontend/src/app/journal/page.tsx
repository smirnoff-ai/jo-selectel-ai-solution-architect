import { Suspense } from "react";

import { JournalView } from "@/components/journal-view";

export default function JournalPage() {
  return (
    <Suspense fallback={<p className="px-6 py-10 text-muted-foreground">Загружаем журнал…</p>}>
      <JournalView />
    </Suspense>
  );
}
