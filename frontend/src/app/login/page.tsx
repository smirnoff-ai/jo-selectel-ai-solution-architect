"use client";

import { type FormEvent, useState } from "react";
import { useRouter } from "next/navigation";

export default function LoginPage() {
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);
  const [pending, setPending] = useState(false);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const login = String(form.get("login") ?? "").trim();
    const password = String(form.get("password") ?? "");
    if (login.length === 0 || password.length === 0 || pending) {
      return;
    }
    setPending(true);
    setError(null);
    const response = await fetch("/api/v1/auth/login", {
      method: "POST",
      headers: { "content-type": "application/json" },
      credentials: "same-origin",
      body: JSON.stringify({ login, password }),
    });
    setPending(false);
    if (!response.ok) {
      setError("Неверный логин или пароль");
      return;
    }
    router.push("/desk");
  }

  return (
    <main className="mx-auto flex min-h-full w-full max-w-sm flex-col justify-center px-6 py-16">
      <h1 className="font-serif text-3xl">Рефлекс</h1>
      <p className="mt-2 text-sm text-muted-foreground">Вход диспетчера</p>
      <form className="mt-8 flex flex-col gap-4" method="post" onSubmit={onSubmit}>
        <label className="flex flex-col gap-1 text-sm">
          Логин
          <input
            name="login"
            autoComplete="username"
            required
            className="rounded-md border border-border bg-card px-3 py-2 text-card-foreground outline-none focus-visible:ring-2 focus-visible:ring-ring"
          />
        </label>
        <label className="flex flex-col gap-1 text-sm">
          Пароль
          <input
            name="password"
            type="password"
            autoComplete="current-password"
            required
            className="rounded-md border border-border bg-card px-3 py-2 text-card-foreground outline-none focus-visible:ring-2 focus-visible:ring-ring"
          />
        </label>
        {error ? <p className="text-sm text-destructive">{error}</p> : null}
        <button
          type="submit"
          disabled={pending}
          className="rounded-md bg-primary px-3 py-2 text-sm text-primary-foreground disabled:opacity-50"
        >
          Войти
        </button>
      </form>
    </main>
  );
}
