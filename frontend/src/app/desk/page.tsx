"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { ThemeToggle } from "@/components/theme-toggle";

export default function DeskPage() {
  const router = useRouter();
  const [login, setLogin] = useState<string | null>(null);

  useEffect(() => {
    void fetch("/api/v1/auth/me", { credentials: "same-origin" }).then(async (response) => {
      if (!response.ok) {
        router.replace("/login");
        return;
      }
      const body = (await response.json()) as { login: string };
      setLogin(body.login);
    });
  }, [router]);

  async function logout() {
    await fetch("/api/v1/auth/logout", { method: "POST", credentials: "same-origin" });
    router.replace("/login");
  }

  if (login === null) {
    return (
      <main className="mx-auto max-w-5xl px-6 py-10">
        <p className="text-muted-foreground">Проверяем сессию…</p>
      </main>
    );
  }

  return (
    <main className="mx-auto flex w-full max-w-5xl flex-col gap-8 px-6 py-10">
      <header className="flex items-center justify-between gap-4">
        <h1 className="font-serif text-3xl">Стол</h1>
        <div className="flex items-center gap-3">
          <span className="text-sm text-muted-foreground">{login}</span>
          <ThemeToggle />
          <button
            type="button"
            onClick={() => void logout()}
            className="rounded-md border border-border px-3 py-1.5 text-sm"
          >
            Выход
          </button>
        </div>
      </header>
      <p className="text-muted-foreground">
        Виджеты появятся в спринте обращений. Сейчас достаточно войти и увидеть этот экран.
      </p>
    </main>
  );
}
